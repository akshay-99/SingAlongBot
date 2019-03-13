
var sender_id=null

$('body').ready(function() {
    //res('Hi!')
    url='/initiate'
    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            
        },
        }).then(response=>{
            response.json().then(
                res=>{
                    console.log(res);
                    sender_id = res.sender_id;
                }
            )
        
        });
    setInterval(getResponses, 1000);
  });
function getResponses()
{
    tosend = {
        sender_id:sender_id
    };
    console.log(sender_id);
    url='/get_pending'
    fetch(url, {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(tosend)
    }).then(response=>{
        response.json().then(
            resp=>{
                count = resp.count;
                msgs = resp.msgs;
                console.log(resp);
                for(var i = 0; i<count; i++)
                    res(msgs[i]);
                
            }
        )
    
    });
    
}
  function sender() {
    var msg = $('.txt1').val();
    $('.main').append('<div class="txt-div" ><div class="txt msg">'+msg+'</div><div class="time">'+new Date().toLocaleTimeString().slice(0, -3)+'</div></div>');
    $('.txt1').val('');
    $('.chat').scrollTop = $('.chat').scrollHeight;
    url = '/send'
    tosend={
        sender_id:sender_id,
        msg:msg
    }
    fetch(url, {
        method: 'POST',
        headers: {
            
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(tosend)
        }).then(response=>{
            response.text().then(
                res=>{
                    console.log(res);
                }
            )
        
        });
  }
  
  function res(msg) {
    $('.main').append('<div class="txt-div2" ><div class="txt2 msg">'+msg+'</div><div class="time2">'+new Date().toLocaleTimeString().slice(0, -3)+'</div></div>');
  }
  
  //var chat = {"Hi":"Hi","Hi2":"Hi2","Hi3":"Hi3"}
  
  