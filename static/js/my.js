
$('#select').on('click', function(){
        search_click();
    });

function search_click(){
    var word = $('#search_keyword').val();
    var request_url = '';
    if(word == ""){
        return
    }

    request_url = "http://127.0.0.1:8000/?key_word="+word;
    location.assign(request_url);
}