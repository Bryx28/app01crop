function sample(){
var m1 = {
    center: new google.maps.LatLng(14.21, 121.75),
    zoom: 13,
    mapss: google.maps.MapTypeId.HYBRID
}
var m2 = new google.maps.Map(document.getElementById("map"), m1);
}