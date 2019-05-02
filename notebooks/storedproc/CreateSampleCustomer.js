function createSampleCustomer(itemToCreate) {
    var context = getContext();
    var collection = context.getCollection();
    // var newID = function () {
    //     return Math.random().toString(36).substr(2, 12);
    //   };
    console.log("hello world!")
    // console.log(newID());
    var accepted = collection.createDocument(collection.getSelfLink(),
        itemToCreate,
        function (err, documentCreated) {
            if (err) throw new Error('Error' + err.message);
            context.getResponse().setBody(documentCreated.id);
        }
    );    
    if (!accepted) return;
}