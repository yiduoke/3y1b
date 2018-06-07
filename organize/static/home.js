$(document).ready(function(){
    var startButtons = document.getElementsByClassName("startButton");

    function handleTask(e){
	if(this.innerHTML == 'Start Task'){
	    $.ajax({
		type: 'POST',
		url: '/startTask/' + this.previousElementSibling.innerHTML,
		async: false
	    });
	    
	    this.innerHTML = 'Complete Task';
	    setTimeout(this.addEventListener('click', completeTask), 500);
	}
	else{
	    $.ajax({
		type: 'POST',
		url: '/completeTask/' + this.previousElementSibling.innerHTML,
		async: false
	    });
	    
	    this.parentNode.remove();
	}
    }

    for (var i = 0; i < startButtons.length; i++){
	startButtons[i].addEventListener("click", handleTask);
    }
});
