function savecomment(videopk,allcomments) {
	var req = new XMLHttpRequest();
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	var comment = document.getElementById('this_comment').value;
	var data = JSON.stringify({"comments":comment,"video_id":videopk});
	var url = "/addcomment/"
	
	req.onreadystatechange = function () { 
	    if (req.readyState == 4 && req.status == 200) {
	    	var jsonstring = req.responseText
	    	if (jsonstring === "Please Type Something In The Comment Box"){
	    		alert(jsonstring);
	    	}
	    	else {
	    		var jsn = JSON.parse(jsonstring);
	  
	    		document.getElementById('comment_box').innerHTML += '<div style="display: flex;">\
	    						<div><img class= channelThumbnail src='+jsn["profile"]+' style="margin-top: 9px;"></div>\
	    						<div style="margin-left: 1%;">\<h5 style="margin-bottom: 0;">\
	    						<b>'+jsn["fullname"]+'</b></h5><p>'+jsn["comment"]+'</p></div></div>';
	    		
	    		document.getElementById('allcomments').innerHTML = parseInt(allcomments)+1+" Comments"
	        	alert("Your Comment is Added")
	        }
	    }
	}
	req.open('POST',url, true);
	req.setRequestHeader("X-CSRFToken", csrftoken); 
	req.setRequestHeader("Content-Type", "application/json"); 
	req.send(data);
	comment = document.getElementById('this_comment').value = '';
}


function subscribe(video_user_id, subcount){
	var sub_btn = document.getElementById('subs_btn')
	
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	var dataa = JSON.stringify({"channel_owner":video_user_id, "count":parseInt(subcount)+1});
	$.ajax({
	type: "POST",
	url: "/subscription/",
	headers: {'X-CSRFToken': csrftoken},
	data: dataa,
	contentType: 'application/json',
	success: function (result) {
		sub_btn.style.background = "gray";
		sub_btn.innerHTML = "SUBSCRIBED"
		document.getElementById('subcount').innerHTML = parseInt(subcount)+1+" subscribers";
		alert(result);
	},
	error: function(result){
		alert(result.responseText);
	}
	});
	
}
var counter = '/loadmore/'
function loadmore(){
	var load_more = document.getElementById('load_more')
	$.ajax({
	type: "GET",
	url: counter,
	beforeSend:function(){
		$("#load_more").attr('disabled','disabled').text('Loading..');
	},
	success: function (result) {
		var _html='';
		$.each(result.results, function(key, value) {
			_html += '<div class="col-lg-3 col-md-4 col-sm-6" style="position: static; padding-right: 5px; padding-left: 5px;">\
        			<div class="youtubeVideo">\
            			<a href="/video/'+String(value["id"])+'/">\
            				<img class= videoThumbnail src ="'+value["video_thumbnail"]+'">\
            			</a>\
             			<div class= videoDetails >\
                			<a href="/allchannel/'+value["user"]+'/">\
                				<img class= channelThumbnail src="'+value["channel_photo"]+'">\
                			</a>\
                			<div class= videoDetailsText >\
			                	<p class= videoTitle >'+value["video_title"]+'</p>\
			               		<p class= channelName >'+value["channel_name"]+'</p>\
			               		<p class= videoViews >'+value["view_time_since"]+'</p>\
               				</div>\
              			</div>\
        			</div>\
    			</div>'
		})
		$(".columncount").append(_html);
		$("#load_more").removeAttr('disabled').text('Load More');
		if (result['next'] === null) {
			load_more.style.display = "none";
		}
		counter = result["next"];
	},
	error: function(result){
		alert(result);
	}
	});
}

loadmore()

function addlike(videopk,likecount,action,lkornot) {
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	if (action === "add"){
		var dataa = JSON.stringify({"video_id":videopk,"like":true});
		$.ajax({
			type: "POST",
			url: "/likevideo/",
			headers: {'X-CSRFToken': csrftoken},
			data: dataa,
			contentType: 'application/json',
			success: function (result) {
				document.getElementById('all_likes').innerHTML = parseInt(likecount)+1;
				document.getElementById('like_add').style.fill = "blue";
				alert(result);
			},
			error: function(result){
				alert(result);
			}
		});
	}

	else{
		if(lkornot === "True"){
			var dataa = JSON.stringify({"video_id":videopk,"like":"False"});
		}
		else{
			var dataa = JSON.stringify({"video_id":videopk,"like":"True"});
		}
		$.ajax({
			type: "PUT",
			url: "/likevideo/",
			headers: {'X-CSRFToken': csrftoken},
			data: dataa,
			contentType: 'application/json',
			success: function (result) {
				if (result["added"] === "like is added"){
					document.getElementById('all_likes').innerHTML = parseInt(likecount)+1;
					document.getElementById('like_change').style.fill = "blue";
					alert(result);
				}
				else{
					document.getElementById('all_likes').innerHTML = parseInt(likecount)-1;
					document.getElementById('like_remove').style.fill = "black";
					alert(result);
				}
			},
			error: function(result){
				alert(result);
			}
		});
	}
}


function change() {
	let changer = document.getElementById('sidebarMenu');
	let video_distance = document.getElementById('visec')
    if (changer.style.width==="14%"){
        changer.style.width="3.4%";
        video_distance.style.marginLeft="9%";
    }
    else{
        changer.style.width="14%";
        video_distance.style.marginLeft="13.8%";
    }
}

var popup1 = document.getElementById("popup-1");
var openPopup1 = document.getElementById("open-popup-1");
var closePopup1 = document.getElementById('close-popup-1');
var video = document.getElementById("myvideo");
if (openPopup1){
	openPopup1.addEventListener('click', function() {
		popup1.style.display = "block";
		video.removeAttribute("controls");
	})
}

if (closePopup1){
	closePopup1.addEventListener('click', function() {
		popup1.style.display = "none";
		video.setAttribute("controls","controls");
	})
}


$(".show-more button").on("click", function() {
    var $this = $(this); 
    var $content = $this.parent().prev("div.content");
    var linkText = $this.text().toUpperCase(); 
    if(linkText === "SHOW MORE"){
        linkText = "SHOW LESS";
        $content.switchClass("hideContent", "showContent");
    }
    else {
        linkText = "SHOW MORE";
        $content.switchClass("showContent", "hideContent");
    };
    $this.text(linkText);
})







