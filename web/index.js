// if browsing with safari then the bottom navigation bar of safari blocks the buttons so I elevate them a little so that I can see them when using the app
if (
  navigator.userAgent.includes("iPhone") &&
  navigator.userAgent.includes("Safari")
) {
  const buttonsElement = document.getElementById("buttons");
  buttonsElement.style.marginBottom = "10vh";
}

const options = {
  zone: document.getElementById("joystick-zone"),
  color: "rgb(14 116 144)",
};

let manager = nipplejs.create(options);
let ws = new WebSocket("ws://10.0.0.170:50000");
let position;
let interval;

manager
  .on("start", () => {
    interval = setInterval(() => {
      ws.send(
        JSON.stringify({
          type: "MouseMove",
          direction: position.angle.degree,
        })
      );
    }, 100);
  })
  .on("move", (_, data) => {
    position = data;
  })
  .on("end", () => {
    clearInterval(interval);
  });

let handleClick = (side) => {
  ws.send(
    JSON.stringify({
      type: "MouseClick",
      side,
    })
  );
};

window.onbeforeunload = () => {
  ws.close(1000);
};
