
var sender_id=null
var socket=null;
$('body').ready(function() {
    $('#ta-msg')[0].disabled=true;
    $('#ta-msg')[0].value="Connecting...";
    var prefix = 'https://';
    if (location.protocol != 'https:')
    {
        prefix = 'http://'
    }
    
    socket = io.connect(prefix + document.domain + ':' + location.port);
    
    socket.on('connect', ()=>{
        $('#ta-msg')[0].disabled=false;
        $('#ta-msg')[0].value="";
        console.log('connected');
    });
    socket.on( 'reply', function(msg)
    {
        res(msg.msg);
    });
});

function sender() {
    var msg = $('.txt1').val();
    $('.main').append('<div class="txt-div" ><div class="txt msg">'+msg+'</div><div class="time">'+new Date().toLocaleTimeString().slice(0, -3)+'</div></div>');
    $('.txt1').val('');
    $('.chat').scrollTop = $('.chat').scrollHeight;
    
    socket.emit( 'user sent', {
        
        msg : msg
    });
}
  
function res(msg) {
    $('.main').append('<div class="txt-div2" ><div class="txt2 msg">'+msg+'</div><div class="time2">'+new Date().toLocaleTimeString().slice(0, -3)+'</div></div>');
}
  

  
  