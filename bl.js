d3.json('http://127.0.0.1:5000/selected_bl').then(function(response){
    trace={
        'x': response['Category'], 
        'y': response['Slope'], 
        'type': 'bar', 
    }
    Plotly.newPlot('bubble', [trace])
})