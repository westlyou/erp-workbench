=================================
Intoduction to the Preset-Manager
=================================
Syntax definition of yaml:
    https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html

A preset is a yaml file describing an object, that has to be created 
in new erp site.

Each preset consists of at least the following elements:

    - Name of the object to create
        The name is descriptive only, but should hint at what
        the objects usage is.
    - model
        This is the erp model used to create the new object
    - model_help
        an explanation of the object
    - handler (optional)
        This is the name of the method that is used to create the object.
        It needs to be accessible within the manager.
        If no handler is provided, a simple base handler is used.

Example::

    # in the erp-site create a an object ot typ "bank"
    bank: 
        # use the model "res.bank"
        model: 'res.bank'
        # provide some help to the person providing thae data
        model_help: 'Hier werden Daten zur Bank der von der Firma genutzten Banken erfasst'
        # use the preset-hmanager handler 'read_bank_yaml'
        # this handler is in the folder pointed to by the preset-hmanager configuration
        # run presets/
        handler: 'read_bank_yaml'

Dependant handlers:
-------------------

A handler can depend from an other handler. Such a handler usualy uses objects
that have been created by the parent handler.

I the following example, creates a parent handler two bank objects.
The dependant handler adds a bank account for each of them.

The dependant handler can access the objects created by the parent handler
using the parents result.

**all** handler depend on the base_preset, and can assume, that all elements it is
responsible for have been created.

Example with dependant handler::

parent::

    bank:
        model: 'res.bank'
        model_help: 'Hier werden Daten zur Bank der von der Firma genutzten Banken erfasst'
        handler: 'read_yaml_bank'
    
    banks:
        bank1:
            name_help: 'Wähle die Bank aus der Liste der Banken. Diese ist auf banks.redo2oo.ch zu finden'
            name: 'Bank1'
        bank2:
            name_help: 'Wähle die Bank aus der Liste der Banken. Diese ist auf banks.redo2oo.ch zu finden'
            name: 'Bank2'

dependent::

    bankaccount:
        model: 'res.partner.bank'
        model_help: 'Angaben zu den Bankkonten'
        handler: 'read_yaml_bankaccount'
        depends: 'read_yaml_bank'

        accounts:
            account1:
                bank_id_help: 'Wähle eine der oben definierten Banken. Die erste heisst bank1'
                bank_id: 'bank1'

                bank_name_help: 'Unter diesem Namen erscheint die Bank im Odoo-Backend'
                bank_name: 'Valiant Bank Breitenrain'

                acc_number_help: 'IBAN Konto-Nummer'
                acc_number: 'CH36 0000 0000 0000 0000 0'

            account2:
                bank_id_help: 'Wähle eine der oben definierten Banken. Die zwite heisst bank2'
                bank_id: 'bank2'

                bank_name_help: 'Unter diesem Namen erscheint die Bank im Odoo-Backend'
                bank_name: 'Postfinance'

                acc_number_help: 'IBAN Konto-Nummer'
                acc_number: 'CH26 0000 0000 0000 0000 0'

