import sys, config, logging, datetime
from .frequests import Frequests


# Providers database, Iyzico, Stripe

def get_payment_provider(name=None):
    if name is None:
        name = config.PAYMENT_PROVIDER

    thismodule = sys.modules[__name__]
    return getattr(thismodule, name)


class PaymentProvider:
    def subscribe(self, account):
        # subscribe user to the system
        pass

    def cancel_subscription(self, account):
        pass

    def get_plans(self):
        # returns the plans in the system
        pass

    def get_plan(self, plan_id):
        # return plan with the given id
        pass

    def update_card(self, account):
        # updates the card of the account
        pass

    def create_customer(self, account):
        pass


class Iyzico(PaymentProvider):
    def subscribe(self, account):
        # subscribe user to the system
        pass

    def cancel_subscription(self, account):
        pass

    def get_plans(self):
        # returns the plans in the system
        pass

    def get_plan(self, plan_id):
        # return plan with the given id
        pass

    def update_card(self, account):
        # updates the card of the account
        pass

    def create_customer(self, account):
        pass


try:
    import stripe

    stripe.api_key = config.STRIPE_PRIVATE_KEY
    stripe.max_network_retries = 5
except:
    pass


class Stripe(PaymentProvider):
    def subscribe(self, account):

        pass

    def cancel_subscription(self, account):
        subscription = stripe.Subscription.retrieve(account.subscription_id)
        subscription.delete()

    def get_plans(self):
        from app.credit.models import Plan
        return Plan.query.all()

    def get_plan(self, plan_id):
        from app.credit.models import Plan
        return Plan.query.all()

    def update_card(self, account, form):
        from flask import make_response, jsonify
        card = self.apply_stripe_card(account.stripe_customer_id, form.stripe.data)
        card_error = card.get('error', None)
        if card_error:
            account.save()
            return make_response(jsonify({
                'global': [card_error],
                'code': '400'
            }), 400)
        account.cc_expires = datetime.date(year=card.get('exp_year'), month=card.get('exp_month'), day=1)
        account.save()

    def create_customer(self, account):
        # Create the user's stripe account if not exists already
        if not account.stripe_customer_id or not stripe.Customer.retrieve(account.stripe_customer_id):
            try:
                customer = stripe.Customer.create(email=account.email)
                account.stripe_customer_id = customer.id
            except stripe.error.InvalidRequestError:
                pass
        pass

    ##
    # Applies the credit or plan to the stripe and organization. Charges the customer. If there is no problem returns the charge_id, None otherwise None, make_response
    #
    # price in cents
    ##
    def apply_plan_credit(self, form, account, plan_id, yearly):
        from flask import make_response
        # Create subscription if there is a plan else charge directly
        if plan_id is not None:
            error = self.update_plan(account, plan_id, yearly)

            if error:
                form.errors['global'] = [error]

                return make_response(form.errors_as_json(), 400)

        return None

    ##
    # Updates the plan of the organization, and subscripes to the stripe plan
    ##
    def update_plan(self, account, plan_id, yearly):
        from app.credit.models import Plan
        new_stripe_plan_id = plan_id
        logging.info("Starting plan update for account {0} with {1} and yearly is {2} so stripe plan is {3} !!".format(account.id, plan_id, yearly, new_stripe_plan_id))

        # Customer has selected same plan
        if new_stripe_plan_id == account.stripe_plan_id:
            return None

        try:
            coupon = None
            trial_period_days = 0
            old_stripe_plan_id = account.stripe_plan_id
            new_stripe_plan = stripe.Plan.retrieve(new_stripe_plan_id)
            new_price = new_stripe_plan.get('amount')  # price in cents

            if old_stripe_plan_id:
                old_subscription = stripe.Subscription.retrieve(account.subscription_id)

                if old_subscription:
                    if not account.yearly:
                        old_plan_amount = int(old_subscription.get('plan').get('amount'))

                        if new_price > old_plan_amount:  # Upgrading subscription
                            coupon_id = '{0}->{1}'.format(old_stripe_plan_id, new_stripe_plan_id)
                            try:
                                coupon = stripe.Coupon.retrieve(coupon_id)
                            except Exception:
                                pass

                            # If there is no existing coupon for this upgrade then create one and use that
                            if not coupon:
                                coupon = stripe.Coupon.create(id=coupon_id, duration="once", amount_off=old_plan_amount, currency="usd")
                        else:  # Downgrading subscription
                            trial_period_days = (datetime.date.fromtimestamp(int(old_subscription.get('current_period_end'))) - datetime.date.today()).days

                        old_subscription.delete()
                    else:  # if yearly subscription exists then cancel all
                        logging.warning("Account {0} requested change of his yearly plan to {1}".format(account.id, new_stripe_plan_id))
                        return "You already have a yearly plan. We do not support automatically upgrade/downgrade of yearly plans. Please contact support!"

            subscription = stripe.Subscription.create(customer=account.stripe_customer_id, items=[{"plan": new_stripe_plan_id}], trial_period_days=trial_period_days, coupon=coupon)

            plan = Plan.find_by_stripe_id(new_stripe_plan_id)
            account.plan_id = plan.id
            account.yearly = yearly
            account.subscription_id = subscription.get('id')
            account.stripe_plan_id = new_stripe_plan_id
            account.save()

            logging.info("Completed plan update for account {0} with {1} and yearly is {2} so stripe plan is {3} !!".format(account.id, plan_id, yearly, new_stripe_plan_id))
        except Exception as e:
            logging.exception("An error occured, Stripe didn't except the subscription for organization id {0} with stripe customer id {1} for plan {2}!!".format(account.id, account.stripe_customer_id, new_stripe_plan_id))

            return "An error occured, Stripe didn't except the subscription !! Detail: {0}".format(str(e))

    def apply_stripe_card(self, stripe_customer_id, card_data):
        logging.debug("api_pay(1.3): Preparing customers cards for stripe id {0}".format(stripe_customer_id))
        # Update the cards of the customer
        response = Frequests.get(
            'https://api.stripe.com/v1/customers/{0}/sources?object=card&limit=100'.format(stripe_customer_id),
            auth=(stripe.api_key, stripe.api_key)
        )

        logging.debug("payment(2): Created plans for the account now entering charge process")
        cards = response.json()
        for card in cards.get('data', []):
            Frequests.delete(
                'https://api.stripe.com/v1/customers/{0}/sources/{1}'.format(stripe_customer_id, card.get('id')),
                auth=(stripe.api_key, stripe.api_key)
            )

        logging.debug("api_pay(1.4): Adding customers card for stripe id {0}".format(stripe_customer_id))
        response = Frequests.post(
            'https://api.stripe.com/v1/customers/{0}/sources'.format(stripe_customer_id),
            auth=(stripe.api_key, stripe.api_key),
            data={
                'source': card_data
            }
        )

        card = response.json()
        if card is None:
            return {'error': 'A fatal error occured with our payment provider.'}

        error_message = card.get('error', {}).get('message', None)
        if error_message is not None:
            logging.warning(response.content)
            return {'error': error_message}

        return card
