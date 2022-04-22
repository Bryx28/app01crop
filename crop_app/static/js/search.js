$(document).ready(function(){
  $('.search').on('keyup',function(){
      var searchTerm = $(this).val().toLowerCase();
      $('#userTbl tbody tr').each(function(){
          var lineStr = $(this).text().toLowerCase();
          if(lineStr.indexOf(searchTerm) === -1){
              $(this).hide();
          }else{
              $(this).show();
          }
      });
  });
});