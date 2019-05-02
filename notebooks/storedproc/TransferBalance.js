function transferBalance(customer_from_id, customer_to_id, amount) {
    var context = getContext();
    var container = context.getCollection();
    var response = context.getResponse();

    var customerFromDocument, customerToDocument;

    // query for first customer
    var filterQuery1 = 
    {     
        'query' : 'SELECT * FROM customers c where c.id = @customer_from_id',
        'parameters' : [{'name':'@customer_from_id', 'value':customer_from_id}] 
    };
            
    var accept = container.queryDocuments(container.getSelfLink(), filterQuery1, {},
        function (err, items, responseOptions) {
            if (err) throw new Error("Error" + err.message);

            if (items.length != 1) throw "Unable to find first customer";
            customerFromDocument = items[0];

            // query for second customer
            var filterQuery2 = 
            {     
                'query' : 'SELECT * FROM customers c where c.id = @customer_to_id',
                'parameters' : [{'name':'@customer_to_id', 'value':customer_to_id}] 
            };
            var accept2 = container.queryDocuments(container.getSelfLink(), filterQuery2, {},
                function (err2, items2, responseOptions2) {
                    if (err2) throw new Error("Error" + err2.message);
                    if (items2.length != 1) throw "Unable to find second customer";
                    customerToDocument = items2[0];
                    transferBalanceDoc(customerFromDocument, customerToDocument, amount);
                    return;
                });
            if (!accept2) throw "Unable to find details for second customer, abort ";
        });

    if (!accept) throw "Unable to find details for first customer, abort ";

    // function to add or remove USD
    function addBalance(balance_text, amount) {
        balance_number = Number(balance_text.replace(/[^0-9.-]+/g,""))
        new_balance_number = balance_number + amount
        new_balance_text = new_balance_number.toLocaleString('en-US', { maximumFractionDigits: 2 })
        return "$".concat(new_balance_text)
    }

    // swap the two players’ teams
    function transferBalanceDoc(customer_from, customer_to, amount) {
        customer_to.balance = addBalance(customer_to.balance, amount);
        customer_from.balance = addBalance(customer_from.balance, -1 * amount);

        var accept = container.replaceDocument(customer_from._self, customer_from,
            function (err, itemReplaced) {
                if (err) throw "Unable to update first customer, abort ";

                var accept2 = container.replaceDocument(customer_to._self, customer_to,
                    function (err2, itemReplaced2) {
                        if (err) throw "Unable to second customer, abort"
                    });

                if (!accept2) throw "Unable to update second customer, abort";
            });

        if (!accept) throw "Unable to update first customer, abort";
    }
}