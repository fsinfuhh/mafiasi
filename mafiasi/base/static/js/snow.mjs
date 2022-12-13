'use strict';

const NUM_SNOWFLAKES = 69;
const SNOWFLAKE_COLORS = [[233, 234, 235], [232, 239, 248], [170, 204, 255], [211, 219, 236]];

let xpos;
let canvas;
let canvas_ctx;
let snowflakes = [];

/**
 * @param a {number}
 * @param b {number}
 * @returns {number} a random number between a and b
 */
function range(a, b) {
    return ~~((b - a) * Math.random() + a)
}

/**
 * @param x {number}
 * @param y {number}
 * @param r {number}
 * @param style {string | CanvasGradient | CanvasPattern}
 */
function drawCircle(x, y, r, style) {
    canvas_ctx.beginPath();
    canvas_ctx.arc(x, y, r, 0, 2 * Math.PI, false);
    canvas_ctx.fillStyle = style;
    canvas_ctx.fill();
}

class Snowflake {
    constructor() {
        this.style = SNOWFLAKE_COLORS[range(0, SNOWFLAKE_COLORS.length)];
        this.r = range(2, 6);
        this.replace();
    }

    /**
     * Called when the snowflake expired and needs to be placed somewhere else with random data
     */
    replace() {
        this.opacity = 0;
        this.dop = 0.03 * range(1, 4);
        this.x = range(-this.r * 2, canvas.width - this.r * 2);
        this.y = range(-20, canvas.height - this.r * 2);
        this.xmax = canvas.width - this.r;
        this.ymax = canvas.height - this.r;
        this.vx = range(0, 2) + 8 * xpos - 5;
        this.vy = 0.7 * this.r + range(-1, 1);
    }

    draw() {
        let ref;
        this.x += this.vx;
        this.y += this.vy;
        this.opacity += this.dop;
        if (this.opacity > 1) {
            this.opacity = 1;
            this.dop *= -1;
        }
        if (this.opacity < 0 || this.y > this.ymax) {
            this.replace();
        }
        if (!((0 < (ref = this.x) && ref < this.xmax))) {
            this.x = (this.x + this.xmax) % this.xmax;
        }
        drawCircle(~~this.x, ~~this.y, this.r, `rgba(${this.style[0]}, ${this.style[1]}, ${this.style[2]},${this.opacity})`);
    }
}

function animate() {
    window.requestAnimationFrame(animate);
    canvas_ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let j = 0; j < snowflakes.length; j++) {
        snowflakes[j].draw();
    }
}

function onWindowResize() {
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
}

function onMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    xpos = Math.min(e.pageX, rect.width) / rect.width;
}

function onWindowLoad() {
    canvas = document.getElementById("snow-canvas");
    canvas_ctx = canvas.getContext("2d");
    xpos = 0.5;
    onWindowResize();

    for (let i = 0; i < NUM_SNOWFLAKES; i++) {
        snowflakes.push(new Snowflake());
    }

    window.addEventListener("resize", onWindowResize);
    document.addEventListener("mousemove", onMouseMove);
    window.requestAnimationFrame(animate);
}

window.addEventListener("load", onWindowLoad);
