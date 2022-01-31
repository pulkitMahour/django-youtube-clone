
function savecomment(videopk,user,allcomments) {
	var req = new XMLHttpRequest();
	
	var comment = document.getElementById('this_comment').value;

	var data = JSON.stringify({"comment":comment,"video_pk":videopk,"user":user});

	var url = "/addcomment?comment="+data
	
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
	        	
	        }
	    }
	}
	req.open('GET',url, true);
	req.send();
	comment = document.getElementById('this_comment').value = '';
}


function addlike(videopk,likecount) {
	var req = new XMLHttpRequest();
	var data = JSON.stringify({"video_pk":videopk});
	var url = "/likevideo?data="+data

	req.onreadystatechange = function () {
		if (req.readyState == 4 && req.status == 200){
			var string = req.responseText;
			if (string === "you have already like this video") {
				alert(string);
			}
			else{
				document.getElementById('all_likes').innerHTML = parseInt(likecount)+1
			}
		}
	}

	req.open('GET',url,true);
	req.send();
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







