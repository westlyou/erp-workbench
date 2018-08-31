#!bin/python
# -*- encoding: utf-8 -*-



class DummyHandler(object):
    """a dummy so we can test the PrestHandler
    from the command line
    """


class PrestHandler(object):
    """
    A preset is a set of predefined values,
    To maipulate it, a file is generated

    To set them is a multi stage procedure:
    - generate a new base site description using:
        bin/s --add-site NEW_SITE_NAME

        This will generate a file:
            sites_list/global_sites/NEW_SITE_NAME
    - in the site-description uncomment the odoo main modules that should be installed
    - prepare setting the preset values:
        bin/s --prepare-site NEW_SITE_NAME
            sites_list/global_sites_preset/NEW_SITE_NAME
                this files contains a block of values per included odoo module
                each value should be set to a sensible value.
                These Blocks are collected from skeleton/preset/ODOO_MAINE_MODULE

                to edit these values execute the following command:
                    bin/ee  NEW_SITE_NAME

        this will generate the following files:

    - generate the the

    """

    def __init__(self, support_handler=None):
        """

        Arguments:
            support_handler {support_handler object} -- instatiated support handler
                                                        which we can use to access the callers
                                                        environment
        """
        if support_handler:
            self.support_handler = support_handler
        else:
            self.support_handler = DummyHandler()

    def get_preset_values(self, pvals, is_local=False):
        """
        the preset_values are store either in a file when we create a new
        site description, or in the site description itself

        Arguments:
            pvals {dict} -- [dictonary to return path to the preset values]

        Keyword Arguments:
            is_local {bool} -- [set when we deal with a local site description] (default: {False})
        """

        if is_local:
            # read preset values from skeleton and mix it into the site description
            # first we read it an write preset file
            from skeleton.base_preset import BASE_PRESET as base_preset, MODELS_TO_USE as models_to_use
            # base_preset is an ordered dictonary

            # keys define model and field of the preset values
            # a key has two parts that are separated by an undersore:
            # MODEL + _  + FIELD
            # a key kan have a third element, separated by a column like:
            # 'bank_name:1' this form is used,
            # when we have a list of identically structured records
            #
            # the MODEL is looked up in models_to_use
            # so models_to_use.get('bank') yields 'res.bank'

            # the values assigned to the keys are tuples of the form:
            # (key-value, eplanatory string)
            # if the key-value is a string starting with '$', it points to the id
            # of a record created to by an other preset value:
            # given the two following elements:
            # BASE_PRESET['bank_name:1'] = ('Bank1' ...)
            # BASE_PRESET['bankaccount_bank_id:1'] = ('$bank_name:1', ..)
            # here '$bank_name:1' points to the ID of the entry created into the
            # list of banks

            # The values are structured by sections that are started by keys of the form:
            # 'titel_XX' where XX is just some number or string to make the section unique
            # this section is put between two strings of '*'
            # so the entry:
            # BASE_PRESET['titel_6'] = ('Website', 'Angaben zur Firmenwebsite')
            # produces
            # ********************************************
            # Website
            # Angaben zur Firmenwebsite
            # ********************************************

            # non section


PrestHandler()
