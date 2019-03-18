
var session_id=0
var socket=null;
$('body').ready(function() {
    
});

function sender() {
    var msg = $('.txt1').val();
    $('.main').append('<div class="txt-div" ><div class="txt msg">'+msg+'</div><div class="time">'+new Date().toLocaleTimeString().slice(0, -3)+'</div></div>');
    document.body.scrollTop = document.body.scrollHeight;
    $('.txt1').val('');
    $('.chat').scrollTop = $('.chat').scrollHeight;
    url = '/send';
    tosend = {msg: msg, sid:session_id};
    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(tosend)
    }).then(response=>response.json())
    .then(json => {
        msgs = json.msgs;
        session_id= json.sid
        console.log(msgs);
        msgs.forEach(res);
    });
}
  
function res(msg) {
    $('.main').append('<div class="txt-div2" ><div class="txt2 msg">'+msg+'</div><div class="time2">'+new Date().toLocaleTimeString().slice(0, -3)+'</div></div>');
    document.body.scrollTop = document.body.scrollHeight;
}
  

  
  