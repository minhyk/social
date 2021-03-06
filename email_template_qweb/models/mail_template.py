# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, tools, models


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    body_type = fields.Selection(
        [('jinja2', 'Jinja2'), ('qweb', 'QWeb')], 'Body templating engine',
        default='jinja2', required=True)
    body_view_id = fields.Many2one(
        'ir.ui.view', 'Body view', domain=[('type', '=', 'qweb')])
    body_view_arch = fields.Text(related=['body_view_id', 'arch'])

    @api.multi
    def generate_email(self, res_ids, fields=None):
        multi_mode = True
        if isinstance(res_ids, (int, long)):
            res_ids = [res_ids]
            multi_mode = False
        result = super(MailTemplate, self).generate_email(
            res_ids, fields=fields
        )
        for record_id, this in self.get_email_template(res_ids).iteritems():
            if this.body_type == 'qweb' and\
                    (not fields or 'body_html' in fields):
                for record in self.env[this.model].browse(record_id):
                    body_html = this.body_view_id.render({
                        'object': record,
                        'email_template': this,
                    })
                    # Some wizards, like when sending a sales order, need this
                    # fix to display accents correctly
                    if not isinstance(body_html, unicode):
                        body_html = body_html.decode('utf-8')
                    result[record_id]['body_html'] = self.render_post_process(
                        body_html
                    )
                    result[record_id]['body'] = tools.html_sanitize(
                        result[record_id]['body_html']
                    )
        return multi_mode and result or result[res_ids[0]]
