


document.addEventListener("DOMContentLoaded", function(){
    liveSend({'event': 'init'})
});



function liveRecv(data) {
    console.log(data)
    if (!("event" in data)) {
        console.log("Event not found");
        return;
    }

    switch(data.event) {
      case 'pong':
        schedule_ping();
        break;
      case 'update_empty':
        empty_job_list();
        schedule_ping();
        break;
      case 'update':
        if ("jobs" in data) {
          update_all_jobs(data['jobs']);
        }
        schedule_ping();
        break;
    }
}

function schedule_ping() {
	setTimeout(do_ping, 2000);
}

function do_ping() {
    liveSend({'event': 'ping'});
}


function empty_job_list() {
  document.querySelector("#moderation_list").innerHTML = "Waiting for drawings to moderate"
}

function update_all_jobs(jobs) {
  parent = document.querySelector("#moderation_list");
  parent.innerHTML="";
  for (i in jobs) {
    id_string = "moderation-job-" + jobs[i].id;
    div = document.querySelector("#moderation_list #" + id_string);
    if (!div) {
      const div = document.createElement("div");
      img1 = document.createElement("img");
      img1.src = jobs[i].prev_drawing;
      img2 = document.createElement("img");
      img2.src = jobs[i].drawing
      // img1.style="float: left;";
      div.appendChild(img1);
      div.appendChild(img2);
      div.innerHTML += "<button class='btn-accept btn btn-success' type='button' onclick='moderation_accept("+jobs[i].id+");'>accept</button><p>Player="+jobs[i].id_in_subsession+", attempt="+jobs[i].attempt+", error="+jobs[i].error+" </p><button class='btn-reject btn btn-danger' type='button' onclick='moderation_reject("+jobs[i].id+")'>reject</button>";
      div.id = id_string;
      div.job = jobs[i];
      // div.innerHTML = id_string;
      parent.appendChild(div);
    }
    // console.log(div);
    // console.log(id_string);
  }
}

function moderation_accept(id) {
  moderation_update(id, "accept");
}

function moderation_reject(id) {
  moderation_update(id, "reject");
}

function moderation_update(id, status) {
  liveSend({'event': status, 'id': id});
  remove_job(id);
}

function remove_job(id) {
  document.querySelector("#moderation_list #moderation-job-"+id).remove();
}
