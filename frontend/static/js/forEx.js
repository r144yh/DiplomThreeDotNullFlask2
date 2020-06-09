let r = 80

function draw(t){
  let a = (t/100)%(Math.PI*38)
  let pts = [];
  for (let i=0; i<a; i+=0.01){
    pts.push([Math.cos(i)*(r-i/1.5), Math.sin(i)*(r-i/1.5)])
  }
  circle.setAttribute('d', 'M' + pts.join('L'))
  requestAnimationFrame(draw)
}

requestAnimationFrame(draw)