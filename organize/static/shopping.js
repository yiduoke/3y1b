// var item = document.getElementsByClassName("item");
var shopped = document.getElementsByClassName("shopped");
// document.body.getElementsByClassName("itemAndButton")[1].children[0].innerHTML;
var item_and_button = document.body.getElementsByClassName("itemAndButton");

function ebay(e){
	if (this.children.length < 3){
		var obj;
		$.ajax({
			type: 'POST',
			url: '/ebay/' + this.children[0].innerHTML,
			async: false
		}).done(function(response){
			obj = JSON.parse(response);
		    console.log(obj);
		});

		// adding the ebay results to an item entry
		for (var i = 0; i < 5; i++){
			var result = document.createElement("DIV");

			var title = document.createElement("DIV");
			title.setAttribute("class", "title");
			var title_text = document.createTextNode(obj.titles[i]);

			var url_element2 = document.createElement("A");
			url_element2.setAttribute("HREF", obj.urls[i]);
			url_element2.appendChild(title_text);
			title.appendChild(url_element2);
			var new_line = document.createElement("BR");
			title.appendChild(new_line);

			var url = document.createElement("DIV");
			url.setAttribute("class", "url");	
			var url_element = document.createElement("A");
			url_element.setAttribute("HREF", obj.urls[i]);

			var picture = document.createElement("IMG");
			picture.setAttribute("src", obj.pictures[i]);
			picture.setAttribute("width", "100");
			picture.setAttribute("height", "100");

			url_element.appendChild(picture);

			url.appendChild(url_element);

			var price = document.createElement("DIV");
			price.setAttribute("class", "price");
			var url_element = document.createElement("A");
			url_element.setAttribute("HREF", obj.urls[i]);
			var two_places = parseFloat(Math.round(obj.prices[i] * 100) / 100).toFixed(2);
			var price_text = document.createTextNode("$"+two_places);
			price.appendChild(price_text);

			result.appendChild(title);
			result.appendChild(url);
			result.appendChild(price);
			result.appendChild(document.createElement("BR"));
			result.appendChild(document.createElement("BR"));
			
			this.appendChild(result);
		}
	}
	else{
		// for (var i = 2; i < this.children.length; i++){
		// 	this.children[i].innerHTML = '';
		// }
		var head = this.children[2];
		while (head){
			next = head.nextElementSibling;
			head.remove();
			head = next;
		}
		console.log(head.nextElementSibling);
	}
}

function completed(e){
	var obj;
	var shopped_thing = this.parentNode.children[0].innerHTML;
	console.log(this.parentNode.children[0].innerHTML);
	console.log(this.parentNode);
	$.ajax({
		type: 'POST',
		url: '/complete_shopping/' + shopped_thing,
	});
	
	this.parentNode.remove();
}

for (var i = 0; i < item_and_button.length; i++){
    item_and_button[i].addEventListener("click", ebay);
}

for (var i = 0; i < shopped.length; i++){
    shopped[i].addEventListener("click", completed);
}
