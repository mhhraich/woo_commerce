from odoo import models, _


class WooOnboardingConfirmationEpt(models.TransientModel):
    _name = 'woo.onboarding.confirmation.ept'
    _description = 'WooCommerce Onboarding Confirmation'

    def yes(self):

        instance_obj = self.env['woo.instance.ept']
        instance_id = self._context.get('woo_instance_id', False)
        if instance_id:
            instance = instance_obj.browse(instance_id)
            company = instance.company_id
            company.write({
                'woo_instance_onboarding_state': 'not_done',
                'woo_basic_configuration_onboarding_state': 'not_done',
                'woo_financial_status_onboarding_state': 'not_done',
                'woo_cron_configuration_onboarding_state': 'not_done',
                'is_create_woo_more_instance': False
            })
            instance.write({'is_onboarding_configurations_done': True})
            return {
                'effect': {
                    'type': 'rainbow_man',
                    'message': _("Congratulations, You have done All Configurations of Instance : %s" % instance.name),
                }
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def no(self):

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
