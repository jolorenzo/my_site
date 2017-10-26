var paramsURI={};window.location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi,function(str,key,value){paramsURI[key] = value;});

// thanks ! http://stackoverflow.com/questions/2196641/how-do-i-make-jquery-contains-case-insensitive-including-jquery-1-8
jQuery.expr[":"].ContainsIgnoreCase = jQuery.expr.createPseudo(function(arg) {
    return function( elem ) {
        return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

function checkFilter(filterInput,panelToFilterDirectChild,childType){
	if(typeof childType == "undefined"){childType="div";}
	if(typeof panelToFilterDirectChild == "string"){panelToFilterDirectChild=$("#"+panelToFilterDirectChild);}
	$(panelToFilterDirectChild).children(childType).show();
	if(filterInput.value.length>0){
		$(panelToFilterDirectChild).children(childType+":not(.no-filterout):not(:ContainsIgnoreCase('"+filterInput.value+"'))").hide().size();
        $(panelToFilterDirectChild).each(function() {
          id=$(this).closest("table").parent("div").attr('id');
          if (typeof id == "undefined"){
             id=$(this).parent("div").attr('id');
          }
          $("a[href='#"+id+"']>.checkFilterCounter").text(" (" + $(this).children(childType).filter(":ContainsIgnoreCase('"+filterInput.value+"')").size() +")");
        });
	}else{
        $(panelToFilterDirectChild).each(function() {
          id=$(this).closest("table").parent("div").attr('id');
          if (typeof id == "undefined"){
             id=$(this).parent("div").attr('id');
          }
          $("a[href='#"+id+"']>.checkFilterCounter").text("");
        });
	}

}


function lockAllInput(){
	$("input").prop("disabled", true);
	$("textarea").prop("disabled", true);
	$("button").prop("disabled", true);
} //end of lockAllInput

function getJSONFromMarketPlaceFor(hash,callback){
	var marketplaceUrl="http://marketplace.france-bioinformatique.fr:8081/metadata/";
	$.ajax({
		url : "/api/getJson",
		type : "GET",
		accepts: "application/json",
		dataType: "json",
		data : {"url":marketplaceUrl+hash+"?media=json"},
		success : function(json) {
			$.ajax({
				url : "/api/getJson",
				type : "GET",
				accepts: "application/json",
				dataType: "json",
				data : {"url":marketplaceUrl+hash+"/"+json.aaData[0][4]+"/"+json.aaData[0][6]+"?media=json"},
				success : function(json) {
					callback(json);
				},
				error : function(xhr,errmsg,err) {
					console.log(xhr.status + ": " + xhr.responseText);
				}
			});
		},
		error : function(xhr,errmsg,err) {
			console.error(xhr.status + ": " + xhr.responseText);
		}
	});
}

function makeAJAXPopover(elements){
    if( typeof elements == "undefined")
        elements=$('[data-toggle="popover"]');
    elements
    .each(function(){
        var _this = this;
        if($(this).attr("data-content")!=""){
            $(this).popover();
        }else{
        var trigger;
        if(typeof $(this).attr("data-trigger")=="undefined" || $(this).attr("data-trigger")=="")
            trigger = "hover";
        else
            trigger = $(this).attr("data-trigger");
        prop={
            delay: {
               show: "800",
               hide: "300"
            },
            container: 'body',
            placement:function (context, source) {
                if(typeof $(source).attr("data-placement")=="undefined" || $(source).attr("data-placement")=="")
                    return "bottom";
                return $(source).attr("data-placement");
            },
            title:function (context, source) {
                if((typeof $(source).attr("title")=="undefined" || $(source).attr("title")=="")
                    && typeof $(source).attr("url")!="undefined")
                    return "<i>loading...</i>";
                return $(source).attr("title");
            },
            content:function (context, source) {
                var obj = $(this);
                if($(obj).attr("data-content")!=""){
                    return $(obj).attr("data-content");
                }
                $.ajax({ url: obj.attr("url"),
                    accepts: "application/json",
                    dataType: "json",
                    success: function(data) {
                        $(obj).attr("data-content",data.content)
                        $(obj).attr("data-original-title",data.title);
                        $(obj).popover('show');
                        $("#"+$(obj).attr("aria-describedby")).addClass($(_this).data("class"));
                    }
                });
                return "<i>loading...</i>";
            },
            trigger:trigger,
            html:true,
        /*}).on("mouseover", function (context, source) {
            var _this = this;
            $(this).popover("show");
            var popover = $("#"+$(this).attr("aria-describedby"));
            popover.on("mouseleave", function () {
                $(_this).popover('hide');
            })
            ;
        }).on("mouseleave", function (context, source) {
			if (typeof $(this).attr("aria-describedby") == "undefined"){return;}
            var _this = this;
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    $(_this).popover("hide");
                }
            }, 800);*/
        };
        if ((trigger == "click hover" || trigger == "hover click") && typeof $(this).attr("data-footer") == "undefined"){
            prop['template']='<div class="popover"><div class="arrow"></div>'
            + '<h3 class="popover-title"></h3>'
            + '<div class="popover-content"></div>'
            + '<h3 class="popover-footer text-right"><i>'+('Click to keep it visible')+'</i></h3>';
        }


        $(this).popover(prop);
        }
    });
}

function addLoadEvent(func) {
    var oldonload = window.onload;
    if (typeof window.onload != 'function') {
        window.onload = func;
    } else {
        window.onload = function() {
            if (oldonload) {
                oldonload();
            }
            func();
        }
    }
}

addLoadEvent(function () {
    $(".inputclear").click(function(e){
        $(e.currentTarget).siblings("input[type=text]").val('');
        $($(e.currentTarget).siblings("input[type=text]")).change();
    });
});

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname, default_value) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    if (typeof default_value == "undefined")
        return "";
    return default_value;
}

function fade_in_out(o,c){
    $(o).animate({
      backgroundColor: c
    }, 2000 ).animate({
      backgroundColor: ""
    }, 6000 );
}

function blink(o,c,cpt){
    if (typeof cpt == "undefined")
        cpt=5;
    $(o).animate({
      backgroundColor: c
    }, 400 ).animate({
      backgroundColor: ""
    }, 400 , function () {if (cpt>1)blink(o,c,cpt-1)});
}