$(document).ready(function(){
    var startButtons = document.getElementsByClassName("startButton");
    
    function handleTask(e){
	if(this.innerHTML == 'Start Task'){
	    var task = this.parentNode.parentNode.firstElementChild.firstElementChild.innerHTML
	    $.ajax({
		type: 'POST',
		url: '/startTask/' + task,
		async: false
	    });
	    
	    this.innerHTML = 'Complete Task';
	    
	    var progressBar = document.createElement('div');
	    progressBar.innerHTML = '<div class="progress col-sm-2" style="padding-left: 0px; padding-right: 0px; "><div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%; background-color:hsl(120,100%,50%);"></div></div>';

	    var url = '/getTimes/' + task;
	    $.get(url, function(d) {
		var times = $.parseJSON(d);
		var startTime = times[0];
		startTimes[task] = new Date(startTime[0], startTime[1]-1, startTime[2], startTime[3], startTime[4], startTime[5], startTime[6]);
		
		var expectedTime = times[1];
		expectedTimes[task] = expectedTime;
	    });
	    
	    this.parentNode.parentNode.appendChild(progressBar.firstChild);
	    bars = document.getElementsByClassName('progress');
	}
	else{
	    var task = this.parentNode.parentNode.firstElementChild.firstElementChild.innerHTML
	    $.ajax({
		type: 'POST',
		url: '/completeTask/' + task,
		async: false
	    });
	    
	    this.parentNode.parentNode.remove();
	}
    }

    for (var i = 0; i < startButtons.length; i++){
	startButtons[i].addEventListener("click", handleTask);
    }
});

var bars = document.getElementsByClassName('progress');
var startTimes = {};
var expectedTimes = {};

function getColor(value){
    if(value >= 100) return 'hsl(0,100%,50%)';
    //value from 0 to 100
    value /= 100;
    var hue=((1-value)*120).toString(10);
    return ["hsl(",hue,",100%,50%)"].join("");
}

function animateBars(){
    for(var i = 0; i < bars.length; i++){
	var bar = bars[i];
	var task = bars[i].parentNode.firstElementChild.firstElementChild.innerHTML;
	
	if(!isNaN(startTimes[task])){
	    var startTime = startTimes[task];
	    var elapsedTime = Date.now() - startTime;
	    var expectedTime = expectedTimes[task];
	    var percent = (elapsedTime / (expectedTime*60*1000)) < 1 ? (elapsedTime / (expectedTime*60*1000)) * 100 : 100;
	    
	    bar.firstElementChild.style.width = percent.toString() + '%';
	    bar.firstElementChild.style.backgroundColor = getColor(percent);
	}
    }
}

setInterval(animateBars, 1000);
