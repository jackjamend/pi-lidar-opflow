const spawn = require('child_process').spawn;
const py = spawn('python3', ['Controller.py']);

const speed = 0.1;
var ev = '';
const readline = require('readline')
readline.emitKeypressEvents(process.stdin);
process.stdin.setRawMode(true);

const arDrone = require('ar-drone');
console.log("ar drone made");
const client = arDrone.createClient();
console.log("client made");

function sleep(time, callback) {
    var stop = new Date().getTime();
    while(new Date().getTime() < stop + time) {
        ;
    }
    callback();
}

client.takeoff();
console.log("taking off");
//anytime we info back this process should be done.
py.stdout.on('data', function(data){
  ev = data.toString().trim();

    if(ev == "left"){
      client.counterClockwise(speed);
      console.log("turn left")
    }
    else if(ev == "right"){
      client.clockwise(speed);
      console.log("turn right")
    }
  else{
//    console.log('Math shit');
    rads = ev*(Math.PI/180)
    console.log(rads);
    if(ev>=0 & ev<=90){
      move(Math.cos(rads), Math.sin(rads))
      //(Math.cos(rads),0,0,Math.sin(rads));
      console.log('1',rads);
    }else if (ev>90 & ev<=180){
      move(Math.cos(rads), Math.sin(rads))
      //move(0,Math.abs(Math.cos(rads)),0,Math.sin(rads));
      console.log('2',rads);
    }else if (ev>180 & ev<=270){
      move(Math.cos(rads), Math.sin(rads))
      //move(0,Math.abs(Math.cos(rads)),Math.abs(Math.sin(rads)),0);
      console.log('3',rads);
    }else if (ev>270 & ev<=360){
      move(Math.cos(rads), Math.sin(rads))
      //move(Math.cos(rads),0,Math.abs(Math.sin(rads)),0);
      console.log('4',rads);
    }
    setTimeout(function(){
    client.stop();
},500)
  }
});

py.stdout.on('end', function(){
  client.stop();
  client.land();
  console.log("landing");
});

function move(f,r){
  client.front(f);
  client.right(r);
};

process.stdin.on('keypress', (str, key) => {
  if (key.ctrl && key.name === 'c') {
    client.stop();
    client.land();
    process.exit();
  } else {
    try {
      keyReturn(str, key);
    } catch (error) {
      console.error(error);
      client.stop();
      client.land();
    }
  }
});

function keyReturn(str, key) {
  if (key.name === 'w') {
    up = client.up(speed);
    console.log('Move Up',up);
  } else if (key.name === 'a') {
    conter_clockwise = client.clockwise(-speed);
    console.log('Turn Counter-Clockwise', Math.abs(conter_clockwise));
  } else if (key.name === 'd') {
    clockwise = client.clockwise(speed);
    console.log('Turn Clockwise', clockwise);
  } else if (key.name === 's') {
    down = client.down(speed);
    console.log('Move Down', down);
  } else if (key.name === 'c') {
    // pngStream = client.getPngStream();
    // pngStream.on('data', console.log);
    // console.log('Png Stream', pngStream);
  } else if (key.name === 'v') {
    video = client.getVideoStream();
    video.on('data', console.log);
    console.log('Video', video);
  } else if (key.name === 'space') {
    stop = client.stop();
    console.log('Stop', stop);
  } else if (key.name === 'escape') {
    land = client.land();
    console.log('Land', land);
    py.kill('SIGINT');
  } else if (key.name === 'tab') {
    takeoff = client.takeoff();
    console.log('Take Off',takeoff);
  } else if (key.name === 'return') {
    // data = client.on('navdata', console.log);
    // console.log('Data', data);
    //
  } else if (key.code === '[A') {
    front = client.front(speed);
    console.log('Move Forward', front);
  } else if (key.code === '[B') {
    back = client.back(speed);
    console.log('Move Backward', back);
  } else if (key.code === '[C') {
    right = client.right(speed);
    console.log('Move Right', right);
  } else if (key.code === '[D') {
    left = client.left(speed);
    console.log('Move Left', left);
  } else {
    console.log(`str: ${str}`);
    console.log(key);
  }
}

function landDrone() {
  client.land();
  console.log('Drone landing');
}

function getInfo(str, key) {
  console.log(`You pressed the ${str} key`);
  console.log();
  console.log(key);
  console.log();
}

console.log("starting program");
/*process.stdin.on('keypress', (str,key)=>{
    if(key && key.name =='t') {
      console.log("taking off!");
    } else if(key && key.ctrl && key.name == 'c') {
      process.exit();
    } else {
      console.log(`You pressed the "$[str]" key`);
    }
  })
*/
