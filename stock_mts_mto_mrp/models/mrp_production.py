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
        routes = {k: v for d in [
            {moves.id: moves.product_id.route_ids |
             moves.product_id.route_from_categ_ids}
            for moves in self.move_raw_ids] for k, v in d.items()}
        this_object = self.env['procurement.rule']
        pulls = [{move.id: this_object.search([
            ('route_id', 'in', routes.get(move.id).ids),
            ('location_src_id', '=', move.location_id.id),
            ('location_id', '=', move.location_dest_id.id)
        ], limit=1)} for move in self.move_raw_ids]
        pulls = {k: v for d in pulls for k, v in d.items()}
        for move in self.move_raw_ids:
            pull = pulls.get(move.id)
            if pull.procure_method == 'make_to_order':
                move.procure_method = pull.procure_method
            elif not pull and mto_route & routes.get(move.id):  # If there is no make_to_stock rule either # noqa
                move.procure_method = 'make_to_order'
