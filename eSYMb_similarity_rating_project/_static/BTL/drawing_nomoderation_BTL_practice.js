
// Drawing surface initial implementation by Peter Vahlgren from CHC


function getDistance(point1, point2){
    let x = Math.abs(point2.x - point1.x);
    let y = Math.abs(point2.y - point1.y);
    return Math.sqrt(x * x + y * y);
}


function getOriginalClick(l) {
	// l should be a <div class="line"> element
	let c = l.cloneNode();
	c.style.transform = "";

	let pos = {
		x: parseFloat(c.style.left), 
		y: parseFloat(c.style.top)
	};

	c.remove()
	return pos;
}


function getOriginalFarEnd(o, rotate = 0) {
	// let o = getOriginalClick(l);
	return {
		x: o.x + lineLength * Math.cos(rotate),
		y: o.y + lineLength * Math.sin(rotate),
	}; 		
}

// debugging

// checking if line is out of bounds

function checkLineOutOfBounds(line,canvas) {
	let linebounds = line.getBoundingClientRect()
	let canvasBounds = canvas.getBoundingClientRect()

	if (linebounds.left < canvasBounds.left ||
		linebounds.right > canvasBounds.right ||
		linebounds.top < canvasBounds.top ||
		linebounds.bottom > canvasBounds.bottom) {
		
		return true;
		}

		return false;
	}

// function checkLineOutOfBounds(line,canvas) {
// 	let linebounds = line.getBoundingClientRect()
// 	if (linebounds.left < canvasBounds.left) {
// 		// move line right
// 		line.style.left = parseInt(line.style.left) - linebounds.left + canvasBounds.left + "px";
// 	} else if (linebounds.right > canvasBounds.right) {
// 		// move line right
// 		line.style.left = parseInt(line.style.left) - linebounds.right + canvasBounds.right + "px";
// 	}
// 	if (linebounds.top < canvasBounds.top) {
// 		// move line down
// 		line.style.top = parseInt(line.style.top) - linebounds.top + canvasBounds.top + "px";
// 	} else if (linebounds.bottom > canvasBounds.bottom) {
// 		// move line up
// 		line.style.top = parseInt(line.style.top) - linebounds.bottom + canvasBounds.bottom + "px";
// 	}
// }


let lineLength = 215
let drawingDiv = "#canvas";
let canvas;
let canvasBounds;
let line;
let startPos;
let lineCount = 0;
let currentAction = "";
let xoffset = 0;
let yoffset = 0;
let clickedMajorAxis = 0;
let origin;
let oppositeOrigin;
let startPosData = {};
let angleData = {};

let modalTimeout = 1500;


// save the button text
let nextbuttonText = "";


function init_canvas() {
    nextbuttonText =  document.querySelector(".otree-btn-next").innerHTML;
	canvas = document.querySelector(drawingDiv);
	if (document.contains(canvas)) {

		canvasBounds = canvas.getBoundingClientRect();

		canvas.addEventListener('mousedown', (e) => {
			finalizeline(e);

			if (!valid_pattern()) {
				error_message("Select a pattern first. ");
				return;
			}

			if (e.target.className == "canvas") {
				// start drawing a new line

				canvasBounds = canvas.getBoundingClientRect();
				if (lineCount >= 6) {
					return;
				}

				startPos = getCanvasMousePos(e); // log
				line = document.createElement('div');
				line.classList.add('line');
				line.style.left = `${startPos.x}px`;
				line.style.top = `${startPos.y}px`;
				canvas.append(line);
				currentAction = "newline";

			} else if (e.target.className == "line") {
				// calculate where we clicked
				startPos = getCanvasMousePos(e);
				origin = getOriginalClick(e.target); // origin of the line
				clickedMajorAxis = getDistance(origin, startPos); // how far along the line did we click


				// if (clickedMajorAxis < 50) {
				// 	// rotate around the far end
				// 	line = e.target;
				// 	currentAction="rotateline2";
				// 	oppositeOrigin = getOriginalFarEnd(origin, rotate = parseFloat(line.style.transform.slice(7)));
				// } else if (clickedMajorAxis < 175) {
				// 	// start moving the line
				// 	line = e.target;
				// 	xoffset = parseInt(line.style.left) - startPos.x;
				// 	yoffset = parseInt(line.style.top) - startPos.y;
				// 	currentAction="moveline";
				// } else {
				// 	// start rotating the line around the origin
				// 	line = e.target;
				// 	currentAction="rotateline";
				// }



			}
		});

		document.addEventListener("mousemove", (e) => {
			if (!line) {
				return;
			}
			let mousePos = getCanvasMousePos(e);
			if (currentAction == "newline") {
				let length = getDistance(startPos, mousePos);
				line.style.width = `${length}px`;
				// line.style.height = `${length}px`;
				const angle = Math.atan2(mousePos.y - startPos.y, mousePos.x - startPos.x);
				angleVariable = angle;
				line.style.transform = `rotate(${angle}rad) translateY(-50%)`;
				// return angle_variable;
			} // else if (currentAction == "moveline") {
			// 	line.style.left = mousePos.x + xoffset + "px";
			// 	line.style.top = mousePos.y + yoffset + "px";
			// } else if (currentAction == "rotateline") {
			// 	// rotate around origin
			// 	const angle = Math.atan2(mousePos.y - origin.y, mousePos.x - origin.x);
			// 	line.style.transform = `rotate(${angle}rad) translateY(-50%)`;
			// } else if (currentAction == "rotateline2") {
			// 	// rotate around opposite point of origin
			// 	const angle = Math.PI + Math.atan2(mousePos.y - oppositeOrigin.y, mousePos.x - oppositeOrigin.x);
			// 	line.style.top = oppositeOrigin.y + lineLength * Math.sin(Math.PI + angle) + "px";
			// 	line.style.left = oppositeOrigin.x + lineLength * Math.cos(Math.PI + angle) + "px";
			// 	line.style.transform = `rotate(${angle}rad) translateY(-50%)`;

			// }
		});


		function finalizeline(e) {			
			if (!line) {
				return;
			}

			if (currentAction == "newline") {
				let length = getDistance(startPos, getCanvasMousePos(e));
				let finishLine = false;
				line.style.width = lineLength + 'px';
				//console.log("length = ", length); // this is not useful for the analysis
				if (length  < 25) {
					line.remove(); // log coordinates from getCanvasMousePos
				} else if (checkLineOutOfBounds(line, canvas)) {
					line.remove();
				} else {
					finishLine = true;
				}

				if (finishLine) {
					lineCount++;
					
					// testing the logging of variables
					// console.log("angle = ", angleVariable, `lineNumber = ${lineCount}`); 
					// console.log("startPos = ", startPos, `lineNumber = ${lineCount}`);
					
					// adding variables to data structures
					startPosData[`line ${lineCount} startPos`] = startPos;
					angleData[`line ${lineCount} angle`] = angleVariable;

					// sending the data structures back to Otree
					document.getElementById('startPosData').value = JSON.stringify(startPosData);
					document.getElementById('angleData').value = JSON.stringify(angleData);
				}
				

			// checkLineOutOfBounds(line);
			// console.log(checkLineOutOfBounds(line));
			line = undefined;
			startPos = undefined;
			currentAction = "";

			} // else if (currentAction == "moveline") {
			// 	checkLineOutOfBounds(line);
			// 	line = undefined;
			// 	startPos = undefined;
			// 	currentAction = "";
			// } else if (currentAction == "rotateline" || currentAction == "rotateline2") {
			// 	checkLineOutOfBounds(line);
			// 	line = undefined;
			// 	startPos = undefined;
			// 	currentAction = "";
			// 	clickedMajorAxis = 0;
			// 	origin = undefined;
			// 	oppositeOrigin = undefined;
			// }

		}

		document.addEventListener('mouseup', finalizeline);
		// delete line functionality (commented out)
		// canvas.addEventListener('dblclick', (e) => {
		// 	if (e.target.classList.contains('line')) {
		// 		e.target.remove();
		// 		lineCount--;
		// 		if (lineCount < 0) {
		// 			lineCount = 0;
		// 		}
		// 	}
		// });
	}
}


function init_modal() {

	// feedback loop modal
	let modalElem = document.getElementById('modal');
	if (modalElem && js_vars.showmodal) {
		var myModal = new bootstrap.Modal(modalElem, {});
		myModal.show();
		if (js_vars.timeout) {
			setTimeout(() => {myModal.hide()}, js_vars.timeout);
		} else {
			setTimeout(() => {myModal.hide()}, modalTimeout);
		}
	}
}

document.addEventListener("DOMContentLoaded", function(){

    init_canvas(); // the logging could maybe be added as a loop here (or inside the function)
    init_modal();

});


function removeErrors() {
	var errors = document.querySelector(".otree-form-errors");
	if (errors) errors.remove();
}

function deleteDrawing() {
	let lines = document.querySelectorAll("#canvas .line");
	for (var i = 0; i < lines.length; i++) {
		lines[i].remove();
	}
	lineCount = 0;

	// also clear errors about pattern
	removeErrors();

    document.querySelector("#draw #surface #canvas").style.backgroundImage="";
    document.querySelector("button.otree-btn-next").removeAttribute("disabled");
    document.querySelector(".otree-btn-next").innerHTML=nextbuttonText;
}


function grayPatterns() {
	let patterns = document.querySelectorAll("[type=radio] + img");
	for (var i = 0; i < patterns.length; i++) {
		patterns[i].style.opacity = 0.4;
	}
}
function deleteLastLine() {
	document.querySelector("#canvas .line:last-child").remove();
	lineCount--;
	if (lineCount < 0) {
		lineCount = 0;
	}
}

function getCanvasMousePos(e) {
	return { x: e.x - canvasBounds.left, y: e.y - canvasBounds.top }
}


function valid_pattern() {
	var pattern = document.querySelector("#pattern input");
	if ((typeof pattern) == 'undefined' ||
		pattern === null) {
		return true; // theres no pattern input to check on this page
	}
	return (!(typeof forminputs.pattern.checked != 'undefined' && (!forminputs.pattern.checked))
			&& forminputs.pattern.value.length != 0);
}

function error_message(m, reset = true) {
	var errors = document.querySelector(".otree-form-errors");
	if (!errors) {
		errors = document.createElement("div");
		errors.className = "otree-form-errors alert alert-danger";
		const target = document.querySelector(".right").firstChild;
		target.parentNode.insertBefore(errors, target);
	} else {
		if (reset) {
			errors.innerText = "";
		}
	}

	errors.innerText += m;
	errors.scrollIntoView();
}

function submit_drawing_moderation(sendfun) {
       // 2. End Practice
	validate_drawing(sendfun);
}


// this is probably the section where I can log data

// mockup for some javascript that saves the drawing in a form input
function validate_drawing(sendfun) {

	// do client side validation

	valid_linecount = 6;
	// console.log(roundNumber);
	// valid_pattern()

	if (valid_pattern()) {  // data looks valid, lets submit
		html2canvas(document.querySelector(drawingDiv), {
			onclone: function(doc) {
				doc.querySelector(drawingDiv).style['background-image'] = null;
				doc.querySelector(drawingDiv).style['background'] = "rgba(255, 255, 255, 0)";
			},
			backgroundColor: null
		}).then(img => {
			// console.log(svgContext);

			img.toBlob(blob => {
				// console.log(blob);
				var reader = new FileReader();
				reader.readAsDataURL(blob);
				reader.onloadend = function () {
					var base64String = reader.result;
					// console.log(base64String);
					
					document.querySelector("input[name='drawing']").value = base64String;
                    // console.log("hi");
                    // console.log(document.querySelector("input[name='drawing']"));
					document.querySelector("#linecount").value = lineCount;
					//document.querySelector("#startPos").value = startPos.x;
					// console.log('Base64 String - ', base64String);
					sendfun();
                    removeErrors();
				}});
		})
	} else { // something is invalid, lets give an error instead

		error_message("", reset = true);
		
		if (!valid_pattern()) {
			error_message("Select a pattern first. ", reset = false);
		}
		if (!valid_linecount) {
			error_message("Draw exactly 6 lines. ", reset = false);
		}
	}
	
}



function send_drawing_moderation_con3() {
	liveSend({
        'event': "check_drawing",
        'drawing': document.querySelector("input[name='drawing']").value,
        'pattern': document.querySelector("#pattern input[name='pattern']:checked").value});
    start_waiting_for_moderation();
}


function send_drawing_moderation_con2() {
	liveSend({
        'event': "check_drawing",
        'drawing': document.querySelector("input[name='drawing']").value,
        'pattern': document.querySelector("#pattern img.checked").alt});
    start_waiting_for_moderation();
}


function send_drawing_moderation_con1() {
	liveSend({
        'event': "check_drawing",
        'drawing': document.querySelector("#draw input").value,
        'pattern': document.querySelector("#pattern input[name='pattern']:checked").value});
    start_waiting_for_moderation();
}



function send_drawing_moderation_con0() {
	liveSend({
        'event': "check_drawing",
        'drawing': document.querySelector("#draw input").value});
    start_waiting_for_moderation();
}

function submit_send() {
    // document.querySelector("input#linecount").value = lineCount;
    // lineCount = 6;
	// document.querySelector("#draw input#drawing").value = "na";
	document.querySelector('#form').submit();
}
