var total_len = document.getElementById('total').value
var crops = [];
var values = [];
var bkg = [];
var brd = [];
for (var i=0; i<total_len; i++){
    crops.push(document.getElementById('crop_'+ i).getAttribute('name'));
    values.push(document.getElementById('value_'+ i).getAttribute('name'));
    bkg.push(document.getElementById('bkg_'+ i).getAttribute('name'));
    brd.push(document.getElementById('brd_'+ i).getAttribute('name'));
}
var ctx = document.getElementById('cropChart').getContext('2d');
var myChart = new Chart(ctx, {
  type: 'pie',
  data: {
    labels: crops,
    datasets: [{
      label: "# of Votes",
      data: values,
      backgroundColor: bkg,
      borderColor: brd,
      borderWidth: 1
    }]
  },
  options: {}
})
