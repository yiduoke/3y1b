var item = document.getElementsByClassName("item");

function ebay(e){
    var obj;
    $.ajax({
        type: 'POST',
        url: '/ebay/' + this.innerHTML,
        async: false
    }).done(function(response){
        obj = JSON.parse(response);
        console.log(obj);
    });

    // adding the ebay results to an item entry
    for (var i = 0; i < 5; i++){
        var result = document.createElement("DIV");
        result.setAttribute("class", "result");
        var new_line = document.createElement("BR");
        var new_line1 = document.createElement("BR");
        var new_line2 = document.createElement("BR");
        var new_line3 = document.createElement("BR");

        var title = document.createTextNode(obj.titles[i]);
        var price = document.createTextNode(obj.prices[i]);

        var url = document.createElement("A");
        url.setAttribute("HREF", obj.urls[i]);

        var picture = document.createElement("IMG");
        picture.setAttribute("src", obj.pictures[i]);
        picture.setAttribute("width", "100");
        picture.setAttribute("height", "100");
        url.appendChild(picture);

        result.appendChild(title);
        result.appendChild(new_line1);
        result.appendChild(url);
        result.appendChild(new_line2);
        result.appendChild(price);
        this.appendChild(result);

        this.appendChild(new_line3);
    }
}

for (var i = 0; i < item.length; i++){
    item[i].addEventListener("click", ebay);
}