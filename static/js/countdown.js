/**
 * Created by Aaron on 8/29/2016.
 */
//var timeInMinutes = 10;


function getTimeRemaining(endtime){
  var t = Date.parse(endtime) - Date.parse(new Date());
  var seconds = Math.floor( (t/1000) % 60 );
  var minutes = Math.floor( (t/1000/60) % 60 );
  var hours = Math.floor( (t/(1000*60*60)) % 24 );
  var days = Math.floor( t/(1000*60*60*24) );
  return {
    'total': t,
    'days': days,
    'hours': hours,
    'minutes': minutes,
    'seconds': seconds
  };
}

function initializeClock(id, minutes_remaining){
    var timeInMinutes = minutes_remaining;
    var currentTime = Date.parse(new Date());
    var endtime = new Date(currentTime + timeInMinutes*60*1000);
    var clock = document.getElementById(id);
    var minutesSpan = clock.querySelector('.minutes');
    var secondsSpan = clock.querySelector('.seconds');
    function updateClock(){
        var t = getTimeRemaining(endtime);
        minutesSpan.innerHTML = ('0' + t.minutes).slice(-2);
        secondsSpan.innerHTML = ('0' + t.seconds).slice(-2);
        if(t.total<=0){
            clearInterval(timeinterval);
            $('#btn_stop').click();
        }
    }

    updateClock(); // run function once at first to avoid delay
    var timeinterval = setInterval(updateClock,100);
}