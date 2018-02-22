/*这些JS仅为Demo页面，使用此插件时如无需要请不要引入。*/
$(document).ready(function(){
	document.title = $("h1").html();
	$(".dtoggle").slideToggle(0);
	window.scrollToElement = function(elem){
		var top = $(elem).offset().top - ($(window).height() / 2) + ($(elem).outerHeight() / 2);
		$("html, body").animate({
			"scroll-top": top
		}, 400, "swing", function(){
			$(elem).addClass("checkchanged");
			setTimeout(function(){
				$(elem).removeClass("checkchanged");
			}, 200);
		});
	}
	$(".mycheckbox").ios6switch();
	$(".mycheckboxes").ios6switch();
	$(".disabledemo").ios6switch();
	$(".disabledopacitydemo").ios6switch({
		disabledOpacity: 0.75
	});
	$(".dynamicdisabledemo").ios6switch();
	$(".enablebutton").click(function(){
		$(".dynamicdisabledemo").trigger("enable");
	});
	$(".disablebutton").click(function(){
		$(".dynamicdisabledemo").trigger("disable");
	});
	$(".orangeswitch").ios6switch({
		switchonColor: "#FF7A00"
	});
	$(".greenswitch").ios6switch({
		switchonColor: "#0DE900"
	});
	$(".fuchsiaswitch").ios6switch({
		switchonColor: "#FF00FF"
	});
	$(".tealswitch").ios6switch({
		switchonColor: "#008080"
	});
	$(".cyanfuchsiaswitch").ios6switch({
		switchoffColor: "#00FFFF",
		switchonColor: "#FF00FF"
	});
	$(".textcolorswitch").ios6switch({
		switchoffTextColor: "#FF0000",
		switchonTextColor: "#7CFC00"
	});
	$(".thumbcolorswitch").ios6switch({
		thumbColor: "#FFFF00",
		thumbPressedColor: "#DBDB00"
	});
	$(".thumbonoffcolorswitch").ios6switch({
		thumbColor: "#FF7A00",
		thumbPressedColor: "#B35500",
		thumbSwitchonColor: "#FF00FF",
		thumbSwitchonPressedColor: "#B300B3"
	});
	$(".largeswitch").ios6switch({
		size: 40
	});
	$(".smallswitch").ios6switch({
		size: 16
	});
	$(".yesnolabelswitch").ios6switch({
		switchoffText: "off",
		switchonText: "on"
	});
	$(".sounddemo").ios6switch({
		sound: "sounds/unlock.mp3"
	});
	$(".nodragdemo").ios6switch({
		draggable: false
	});
	$(".noanimatedemo").ios6switch({
		animateSpeed: 0
	});
	$(".animatespeeddemo").ios6switch({
		animateSpeed: 1000
	});
	$(".linearanimatedemo").ios6switch({
		animateEasing: "linear"
	});
	$(".showboxdemo").ios6switch({
		showOriginalCheckbox: true
	});
	$(".scriptcontroldemo").ios6switch();
	$(".switchonbutton").click(function(){
		$(".scriptcontroldemo").trigger("switchon");
	});
	$(".switchoffbutton").click(function(){
		$(".scriptcontroldemo").trigger("switchoff");
	});
	$(".scripttoggledemo").ios6switch();
	$(".toggleswitchbutton").click(function(){
		$(".scripttoggledemo").trigger("toggleswitch");
	});
	$(".clickcheckdemo").ios6switch();
	$(".checkbutton").click(function(){
		alert($(".clickcheckdemo")[0].checked);
	});
	$(".changecheckdemo").ios6switch();
	$(".changecheckdemo")[0].onchange = function(){
		$(".checkfield").addClass("checkchanged");
		setTimeout(function(){
			$(".checkfield").removeClass("checkchanged");
		}, 100);
		$(".checkfield")[0].innerHTML = $(".changecheckdemo")[0].checked;
	}
	$(".deletedemo").ios6switch();
	$(".deletebutton").click(function(){
		$(".deletedemo").trigger("destroy");
	});
	$(".ios7styledemo").ios6switch({
		switchonColor: "#64BD63",
		addClass: "ios7style"
	});
	$(".bgtransparentdemo").ios6switch({
		addClass:"transparentbg"
	});
	$(".changesizedemo").ios6switch({
		addClass: "changeSize"
	});
	$(".size20button").click(function(){
		$(".changeSize").animate({
			height: "20px"
		});
	});
	$(".size27button").click(function(){
		$(".changeSize").animate({
			height: "27px"
		});
	});
	$(".size40button").click(function(){
		$(".changeSize").animate({
			height: "40px"
		});
	});
	$(".size50button").click(function(){
		$(".changeSize").animate({
			height: "50px"
		});
	});
	$(".bgcolorstyledemo").ios6switch({
		addClass: "huegradient"
	});
	$(".bgpatterndemo").ios6switch({
		addClass:"patterngradient"
	});
	$(".invertdemo").ios6switch({
		switchonColor: "#FFFFFF",
		switchoffColor: "#008AF2",
		switchonTextColor: "#555555",
		switchoffTextColor: "#FFFFFF",
		switchonText: "0",
		switchoffText: "1"
	});
	$(".invertdemo")[0].onchange = function(){
		$(".invertcheckfield").addClass("checkchanged");
		setTimeout(function(){
			$(".invertcheckfield").removeClass("checkchanged");
		}, 100);
		$(".invertcheckfield")[0].innerHTML = !$(".invertdemo")[0].checked;
	}
});