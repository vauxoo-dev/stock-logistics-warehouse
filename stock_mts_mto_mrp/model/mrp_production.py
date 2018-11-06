# Copyright 2018 Vauxoo, www.vauxoo.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    @api.multi
    def _adjust_procure_method(self):
        """This method is taken from odoo as is from the module mrp. This is
        done because there was no way to interfiere in the decision making
        about what routes to take"""
        try:
            mto_route = self.env['stock.warehouse']._get_mto_route()
        except UserError:
            mto_route = self.env['stock.location.route']
        # This new route is for taking in count this module, the rest is the same as odoo # noqa
        mto_route |= self.env['stock.location.route'].search([
            ('name', 'like', 'Make To Order + Make To Stock')], limit=1)
        for move in self.move_raw_ids:
            product = move.product_id
            routes = product.route_ids | product.route_from_categ_ids
            # TODO: optimize with read_group?
            pull = self.env['procurement.rule'].search([
                ('route_id', 'in', routes.ids),
                ('location_src_id', '=', move.location_id.id),
                ('location_id', '=', move.location_dest_id.id)], limit=1)
            if pull.procure_method == 'make_to_order':
                move.procure_method = pull.procure_method
            elif not pull and mto_route & routes:  # If there is no make_to_stock rule either # noqa
                import pdb;pdb.set_trace()
                origin = (move.group_id and move.group_id.name or (
                    move.rule_id and move.rule_id.name or move.origin or
                    move.picking_id.name or "/"))
                values = move._prepare_procurement_values()
                self.env['procurement.group'].run(
                    move.product_id, move.product_uom_qty, move.product_uom,
                    move.location_id, move.rule_id and move.rule_id.name or
                    "/", origin, values)
