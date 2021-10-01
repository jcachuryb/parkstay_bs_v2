var search_avail = {
    var: { 
           
	   'page': '',
	   'campground_id': null,
	   'camping_period': {'checkin': null, 'checkout': null},
	   'location_url' : '/api/campground_map/?format=json',
	   'search_location_url' : '/api/search_suggest',
           'places_url' : '/api/places/',
           'locations' : [],
           'places': [],
	   'search_locations': [],
	   'campers': {'adult': 0, 'concession':0, 'children':0, 'infant':0, 'total_people': 0},
	   'vehicles': {'vehicle': 0,'campervan': 0, 'motorcycle': 0, 'trailer': 0}
    },
    change_camper_counters: function(group, direction) {
	   
	   if (group in search_avail.var.campers) {

		if (direction == 'up') { 
			search_avail.var.campers[group] = search_avail.var.campers[group] + 1;
		}
	   }

           if (group in search_avail.var.campers) {
                if (direction == 'down') {
                        if (search_avail.var.campers[group] > 0) { 
                        	search_avail.var.campers[group] = search_avail.var.campers[group] - 1;
			}
                }
           }
	   // search_avail.var.campers['total_people']  = search_avail.var.campers['adult'] + search_avail.var.campers['concession'] + search_avail.var.campers['children'];
           //$('#camper-selection-inner-text').html(search_avail.var.campers['adult']+' adult, '+search_avail.var.campers['concession']+' concession, '+search_avail.var.campers['children']+' child, '+search_avail.var.campers['infant']+' Infant');
	   search_avail.total_campers();

           if (search_avail.var.page == 'campsite-availablity') {
            ///   search_avail.load_campsite_availabilty();
           }


    },
    total_campers: function() {
	     search_avail.var.campers['total_people']  = search_avail.var.campers['adult'] + search_avail.var.campers['concession'] + search_avail.var.campers['children'];    
             $('#camper-selection-inner-text').html(search_avail.var.campers['adult']+' adult, '+search_avail.var.campers['concession']+' concession, '+search_avail.var.campers['children']+' child, '+search_avail.var.campers['infant']+' Infant');
    },	    
    change_vehicle_counters: function(group, direction) {

           if (group in search_avail.var.vehicles) {
                if (direction == 'up') {
                        search_avail.var.vehicles[group] = search_avail.var.vehicles[group] + 1;
                }
           }

           if (group in search_avail.var.vehicles) {
                if (direction == 'down') {
                        if (search_avail.var.vehicles[group] > 0) {
                                search_avail.var.vehicles[group] = search_avail.var.vehicles[group] - 1;
                        }
                }
           }

           $('#vehicle-selection-inner-text').html(search_avail.var.vehicles['vehicle']+' vehicle , '+search_avail.var.vehicles['campervan']+' campervans, '+search_avail.var.vehicles['motorcycle']+' motorcycles, '+search_avail.var.vehicles['trailer']+' trailers');

           if (search_avail.var.page == 'campsite-availablity') {
              // search_avail.load_campsite_availabilty();
           }

    },
    get_search_locations: function() {
                $.ajax({
                    url: search_avail.var.search_location_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    data: "{}",
                    success: function(response) {
                            search_avail.var.search_locations = response;
                    },
                    error: function (error) {
                        alert('Error loading search locations');
                    },
                });
    },	   
    get_locations: function() {
                $.ajax({
                    url: search_avail.var.location_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    data: "{}",
                    success: function(response) {
                            search_avail.var.locations = response;
                            // console.log(response);

                    },
                    error: function (error) {
                        alert('Error loading locations');
                    },
                });
    },
    get_places: function() {
                $.ajax({
                    url: search_avail.var.places_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    // data: "{}",
                    success: function (response) {
                            search_avail.var.places = response;
                            // console.log(response);
                    },
                    error: function (error) {
                        alert('Error loading places');
                    },
                });
    },
    close_dropdowns: function() {
	    var vehicledropdown = $('#vehicle-dropdown').css('display');
	    var camperdropdown = $('#camper-dropdown').css('display');
	    if (vehicledropdown == 'none' && camperdropdown == 'none') {
	    } else {
                    search_avail.load_campsite_availabilty();
		    $('#camper-dropdown').hide();
		    $('#vehicle-dropdown').hide();

            }
    },
    vehicle_toggle: function() {
	$('#camper-dropdown').hide();
        var vehicledropdown = $('#vehicle-dropdown').css('display');
        if (vehicledropdown == 'none') {
                 $('#vehicle-dropdown').show();
        } else {
                $('#vehicle-dropdown').hide();
		search_avail.load_campsite_availabilty();
        }
    },
    campers_toggle: function() {
	$('#vehicle-dropdown').hide();
        var camperdropdown = $('#camper-dropdown').css('display');
        if (camperdropdown == 'none') { 
		 $('#camper-dropdown').show();
	} else {
		$('#camper-dropdown').hide();
		search_avail.load_campsite_availabilty();
	}
    },
    select_days_earlier: function(days) {
       var checkin = $('#checkin').val();
       var checkout = $('#checkout').val();

       var checkin_date = Date.parse(checkin);
       var checkout_date =  Date.parse(checkout);
       var checkin_date_moment = moment(checkin_date);
       var checkout_date_moment = moment(checkout_date);
       var checkin_date_moment = checkin_date_moment.subtract(1, 'days');
       var checkout_date_moment = checkout_date_moment.subtract(1, 'days');
       search_avail.init_dateselection(checkin_date_moment.format('YYYY/MM/DD'),checkout_date_moment.format('YYYY/MM/DD'));
    },
    select_days_later: function(days) {
       var checkin = $('#checkin').val();
       var checkout = $('#checkout').val();

       var checkin_date = Date.parse(checkin);
       var checkout_date =  Date.parse(checkout);
       var checkin_date_moment = moment(checkin_date);
       var checkout_date_moment = moment(checkout_date);
       var checkin_date_moment = checkin_date_moment.add(1, 'days');
       var checkout_date_moment = checkout_date_moment.add(1, 'days');
       search_avail.init_dateselection(checkin_date_moment.format('YYYY/MM/DD'),checkout_date_moment.format('YYYY/MM/DD'));
    },
    select_dates: function(start, end) {
        $('#when-date-range #when-dates').html("<b>Arrive:</b> "+start.format('(ddd) D MMM YY') + ' <b>Depart:</b> ' + end.format('(ddd) D MMM YY'));
        $('#checkin').val(start.format('YYYY/MM/DD'));
        $('#checkout').val(end.format('YYYY/MM/DD'));
        search_avail.var.camping_period['checkin'] = start.format('YYYY/MM/DD')
	search_avail.var.camping_period['checkout'] = end.format('YYYY/MM/DD')

        var whennights = search_avail.calculate_nights(start,end);
        $('#when-nights').html(whennights);
	if (search_avail.var.page == 'campground') { 
	   $('#map-reload').click();
	}
	if (search_avail.var.page == 'campsite-availablity') {
	   search_avail.load_campsite_availabilty();
        }
    },
    calculate_nights: function(start,end) {
           oneDay = 24 * 60 * 60 * 1000; 
           diffDays = Math.round(Math.abs((start - end) / oneDay));
           diffDays = diffDays - 1; 
           return diffDays;
    },
    select_remove: function() {
	    $('#search-filters').hide();
            $('#search-selections').hide();

            $('#region-park-selection-outer').hide();
            $('#region-park-selection-inner').html('');
            $('#region-park').val('');
            $('#region-park').show();
    },
    select_region: function(value_id, value_name, coord_1, coord_2, zoom_level) {
	      $('#coord_1').val(coord_1);
	      $('#coord_2').val(coord_2);
	      $('#zoom_level').val(zoom_level);
              $('#search-filters').show();
 	      $('#search-selections').show();
	      // need to open the map first before the campground cards will show
	      search_avail.select_filter_tab('map');
	      search_avail.select_filter_tab('campgrounds');

              $('#region-park-selection-outer').show();
              $('#region-park-selection-inner').html(value_name);
              $('#ps_search_dropdown').remove();
              $('#region-park').hide();
	     
    },
    select_filter_tab: function(tab) {
             $('#card-preview').hide();
	     $('#map-preview').hide();
             $('#card-preview-tab').removeClass('active');
	     $('#map-preview-tab').removeClass('active');

             if (tab == 'campgrounds') {
                  $('#card-preview').show();
		  $('#card-preview-tab').addClass('active');
	     }

	     if (tab == 'map') {
		  $('#map-preview').show();
		  $('#map-reload').click();
		  $('#map-preview-tab').addClass('active');
	     }

    },
    filter_options: function(status) { 
            if (status == 'open') { 
                $('#filter-options').slideDown();
		$('#more-filters').hide();
		$('#hide-filters').show();
            } else {
		$('#filter-options').slideUp();
		$('#hide-filters').hide();
		$('#more-filters').show();
            }

    },
    distance_between_gps: function(lat1, lon1, lat2, lon2, unit) {
	if ((lat1 == lat2) && (lon1 == lon2)) {
		return 0;
	}
	else {
		var radlat1 = Math.PI * lat1/180;
		var radlat2 = Math.PI * lat2/180;
		var theta = lon1-lon2;
		var radtheta = Math.PI * theta/180;
		var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
		if (dist > 1) {
			dist = 1;
		}
		dist = Math.acos(dist);
		dist = dist * 180/Math.PI;
		dist = dist * 60 * 1.1515;
		if (unit=="K") { dist = dist * 1.609344 }
		if (unit=="N") { dist = dist * 0.8684 }
		return dist;
	}
    },
    init_dateselection: function(start,end) { 
        if (start == null) {
            start = moment().add(1, 'days');
	} else {
              var start_date= Date.parse(start);
	      start = moment(start_date);
	}
	if (end == null) {
            end = moment().add(8,'days');
	} else {
            var end_date = Date.parse(end);
	    end = moment(end_date);
	}

        $('#when-date-range').daterangepicker({
            minDate: new Date(),
            startDate: start,
            endDate: end,
            //ranges: {
            //   'Today': [moment(), moment()],
            //   'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            //   'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            //   'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            //   'This Month': [moment().startOf('month'), moment().endOf('month')],
            //   'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            //}
        }, search_avail.select_dates);
        search_avail.select_dates(start,end); 
    }, 
    search_pl: function(e, element_id, element_value) {
            if (element_value.length < 2) {
                $('#ps_search_dropdown').remove();
            } else {

            var search_results = [];
            for (let i = 0; i < search_avail.var.locations.features.length; i++) {
                    if (search_avail.var.locations.features[i].properties.name.toLocaleLowerCase().indexOf(element_value.toLocaleLowerCase())!=-1) {
                          console.log('found');
                          // search_results.push({'id': search_avail.var.locations.features[i].properties.id , 'name': search_avail.var.locations.features[i].properties.name, 'type' :'locations','coord_1' : search_avail.var.locations.features[i].geometry.coordinates[0], 'coord_2': search_avail.var.locations.features[i].geometry.coordinates[1]});
                    }
                   // console.log(search_avail.var.locations.features[i].properties.name);
            }

            for (let i = 0; i < search_avail.var.search_locations.features.length; i++) {
                    if (search_avail.var.search_locations.features[i].properties.name.toLocaleLowerCase().indexOf(element_value.toLocaleLowerCase())!=-1) {
                          console.log('search found');
                          search_results.push({'id': search_avail.var.search_locations.features[i].properties.id , 'name': search_avail.var.search_locations.features[i].properties.name, 'type' :'locations','coord_1' : search_avail.var.search_locations.features[i].coordinates[0], 'coord_2': search_avail.var.search_locations.features[i].coordinates[1], 'zoom_level':search_avail.var.search_locations.features[i].properties.zoom_level});
                    }
                   // console.log(search_avail.var.locations.features[i].properties.name);
            }
            

            for (let i = 0; i < search_avail.var.places.length; i++) {
                     if (search_avail.var.places[i].name.toLocaleLowerCase().indexOf(element_value.toLocaleLowerCase()) != -1) {
                           search_results.push({'id': search_avail.var.places[i].id ,'name': search_avail.var.places[i].name, 'type': 'places', 'coord_1': search_avail.var.places[i].gps[0], 'coord_2': search_avail.var.places[i].gps[1], 'zoom_level': search_avail.var.places[i].zoom_level});
                     }
                      //console.log(search_avail.var.places[i].name);
            }


            if (e.keyCode === 13) {
                if (search_results.length > 0) {
                        search_avail.select_region(search_results[0]['id'],search_results[0]['name'], search_results[0]['coord_1'], search_results[0]['coord_2'], search_avail.var.places[i].zoom_level);
                        // $('#region-park-selection').html(search_results[0]['name']);
                }
            } else {
                // Create list for dropdown
                var search_results_html = "";
                var rowcount =0;

                for (let i = 0; i < search_results.length; i++) {
                        // console.log(search_results[i]['name']+"test");
                        var search_pattern = RegExp(element_value, 'gi');
                        var sr = search_results[i]['name'].match(search_pattern);
                        for (let s = 0; s < sr.length; s++) {
                               var completed = {};
                               var sp = RegExp(sr[s], 'g');

                               search_results[i]['name'] = search_results[i]['name'].replace(sp, "<span>"+sr[s]+"</span>");
                        }
                        if (rowcount < 15) {
                        	search_results_html += "<div id='search_dropdown_item_"+rowcount+"' onclick='search_avail.select_region("+search_results[i]['id']+","+'"'+search_results[i]['name']+'"'+","+'"'+search_results[i]['coord_1']+'"'+","+'"'+search_results[i]['coord_2']+'"'+","+'"'+search_results[i]['zoom_level']+'"'+");'  class='search_dropdown_item_outer'><div class='search_dropdown_item_inner'>"+search_results[i]['name']+"</div></div>";
                            rowcount = rowcount + 1;
                        }
                }

                $('#ps_search_dropdown').remove();
                $('#'+element_id).after("<div id='ps_search_dropdown' class='search_dropdown'><div class='col-sm-12'>"+search_results_html+"</div></div>");

                }
            }
    },
    create_booking: function(button_element) {
	   var databutton = $(button_element).attr('data-button');
	   var button_data = $.parseJSON(databutton);
           var post_data = {};



	   if (button_data['site_type'] == 0) { 
		post_data = {"arrival": search_avail.var.camping_period['checkin'],"departure":search_avail.var.camping_period['checkout'],"num_adult": search_avail.var.campers['adult'],"num_child":search_avail.var.campers['children'],"num_concession": search_avail.var.campers['concession'],"num_infant": search_avail.var.campers['infant'],"campsite": button_data['campsite_id'], 'num_vehicle': search_avail.var.vehicles['vehicle'], 'num_campervan': search_avail.var.vehicles['campervan'], 'num_motorcycle': search_avail.var.vehicles['motorcycle'], 'num_trailer': search_avail.var.vehicles['trailer']}
	   } else {
		post_data = {"arrival": search_avail.var.camping_period['checkin'],"departure":search_avail.var.camping_period['checkout'],"num_adult": search_avail.var.campers['adult'],"num_child":search_avail.var.campers['children'],"num_concession": search_avail.var.campers['concession'],"num_infant": search_avail.var.campers['infant'], "campground": button_data['campground_id'], 'campsite_class': button_data['campsite_class_id'], 'num_vehicle': search_avail.var.vehicles['vehicle'], 'num_campervan': search_avail.var.vehicles['campervan'], 'num_motorcycle': search_avail.var.vehicles['motorcycle'], 'num_trailer': search_avail.var.vehicles['trailer']}
		   // campsite_class: 75
	   }

           $.ajax({
		   url: "/api/create_booking/",
		   cache: false,
		   type: "POST",
		   data: post_data,
		   error: function (request, status, error) {
		 	console.log("Error initing booking creation");	
		   },
		   success: function(data) {
                          if (data['status'] == 'success') {
				window.location = "/booking/";
		          } else {
				console.log("Error");
			  }
		   },
           });

    },
    load_campsite_availabilty: function() { 

	    $("#campsite-availablity-results").html("<center><img style='padding-top: 20px;' height='70' src='/static/ps/img/parkstay_loader_bar_white_500.gif'></center>");
            $.ajax({
            	  url: "/api/campsite_availablity_view/"+search_avail.var.campground_id+"/?arrival="+search_avail.var.camping_period['checkin']+"&departure="+search_avail.var.camping_period['checkout']+"&num_adult="+search_avail.var.campers['adult']+"&num_child="+search_avail.var.campers['children']+"&num_concession="+search_avail.var.campers['concession']+"&num_infant="+search_avail.var.campers['infant']+"&gear_type=all",
            	  cache: false,
		  error: function (request, status, error) {
                        $("#campsite-availablity-results").html("<center><span style='color:red; font-weight:bold;'>Sorry, there was an error loading campsite information.</span></center>");
		  },
            	  success: function(data) {

                          var tents = $('#filter-checkbox-tent').is(':checked');
                          var campervan = $('#filter-checkbox-campervan').is(':checked');
                          var campertrailer = $('#filter-checkbox-campertrailer').is(':checked');

                          var features_checked= new Set();
 
                          var tents = $('#filter-checkbox-tent').is(':checked');
                          var campervan = $('#filter-checkbox-campervan').is(':checked');
                          var campertrailer = $('#filter-checkbox-campertrailer').is(':checked');

                          $("#search-filters-campsites").find("input").each(function() {
                             if (this.id.substring(0,15) == 'filter-feature-') {
                                  var filter_element_id = this.id;
                                  var feature_id = this.id.substring(15);
                                  var is_checked = $("#"+filter_element_id).is(':checked');
                                  if (is_checked == true) {
                                      features_checked.add(parseInt(feature_id));
                                  }
                             }
                          });



			  var campsitehtml = "";
			  var campsitehtmlbefore = "";
			  var campsitehtmlafter = "";
			  var campsitehtmlmiddle = "";
			  var campsitehtmlmiddlestart = "";
			  var campsitehtmlmiddleend = "";

			  var campsitehtmlbox = "";
			  var site_type= data.site_type;
			  var campground_id = data.id;
                          var campsites=data.sites;
                          for (let s = 0; s < campsites.length; s++) {
				campsitehtml = "";
                                var append_site = true;
				var campsite_available = true;
				var campsite_price = parseFloat('0.00');
				var class_name = '';
				var product_box_header_class = 'product-box-header-noavail';
				var priceavail = 'product-available-price-noavail';


                                // Filters Start
                                if (search_avail.var.campers['total_people'] >= campsites[s].min_people && search_avail.var.campers['total_people']  <= campsites[s].max_people) {
                                } else {
                                        append_site = false;
                                }


                                if (append_site == true) {
                                     var gearType = campsites[s].gearType;

                                     if (tents == true && gearType.tent == false) {
                                                append_site = false;
                                     }

                                     if (campervan == true && gearType.campervan == false) {
                                                append_site = false;
                                     }

                                     if (campertrailer == true && gearType.caravan == false) {
                                                append_site = false;
                                     }
                                 }

                                 if (append_site == true) {
                                     var campsite_features = campsites[s].features;
                                     var feats = new Set(campsite_features.map(function(x) {
                                         return x.id;
                                     }));

                                     for (var x of features_checked) {
                                           if (!feats.has(x)) {
                                                append_site = false;
                                           }

                                     }
                                }


				// Filters End  





				for(let p = 0; p < campsites[s].availability.length; p++) {
                                         campsite_price = campsite_price + parseFloat(campsites[s].availability[p][2]);
				         if (campsites[s].availability[p][0] == true) {
					 } else {
                                               campsite_available = false;
					 }
			        }

                                if (campsite_available == true) {

					if (append_site == true) {
					        product_box_header_class = 'product-box-header-avail';
 					        priceavail = 'product-available-price-avail';
					} else {
						product_box_header_class = 'product-box-header-avail-nomatch';
						priceavail = 'product-available-price-avail-nomatch';

					}
			        }
                                if (campsites[s].class)  {
					class_name = " - "+data.classes[campsites[s].class]
				}
				campsitehtml = campsitehtml + "<div class='col-12 col-sm-12 col-md-6 col-lg-6 col-xl-4 col-xxl-3'><center>";
			        campsitehtml = campsitehtml + "<div class='product-box' >";
				campsitehtml = campsitehtml + "<div class='product-box-header "+product_box_header_class+"'><h2>"+campsites[s].name+" "+class_name+"</h2></div>";
				campsitehtml = campsitehtml + "<div><i class='bi bi-person-fill'></i> "+campsites[s].min_people+" to "+campsites[s].max_people+" <img src='/static/ps/img/car.png' style='height:16px;'>  "+campsites[s].max_vehicles+" <img src='/static/ps/img/trailer.png' style='height:16px;'>  "+campsites[s].max_vehicles+"</div>";

				campsitehtml = campsitehtml + "<div class='product-availablity'>";

				for(let f = 0; f < campsites[s].features.length; f++) {
					campsitehtml = campsitehtml + "<div class='product-availablity-features'>"+campsites[s].features[f].name+"</div>";
			 	}
				    
				campsitehtml = campsitehtml + "</div>";
				campsitehtml = campsitehtml + "<div class='product-availablity-short-description'>"+campsites[s].short_description+"</div>";
				campsitehtml = campsitehtml + "<div class='row'>";
				campsitehtml = campsitehtml + "<div class='col-3'>";

				if (campsite_available == true) {
                                     if (append_site == true) {
     				          campsitehtml = campsitehtml + "<i class='bi bi-check-square-fill product-availablity-status product-availablity-selection-green' onfocus='search_avail.show_avail_by_day("+campsites[s].id+")'></i>";
                                     } else {
					  campsitehtml = campsitehtml + "<i class='bi bi-slash-square-fill product-availablity-status product-availablity-selection-grey' ></i>";
				     }
				} else {
			             campsitehtml = campsitehtml + "<i class='bi bi-x-square-fill product-availablity-status product-availablity-selection-red' ></i>";
				}

                                campsitehtml = campsitehtml + "<div id='campsite-availablity-by-day"+campsites[s].id+"' class='product-available-dates-box' >";
				campsitehtml = campsitehtml + "<h4>Availablity</h4>";
				campsitehtml = campsitehtml + "<table cellpadding='0' cellspacing='0' style=''><tr>";
				var availloop =0;
				for(let a = 0; a < campsites[s].availability.length; a++) {
					var da =  campsites[s].availability[a][5];
                                        var dasplit = da.split("-");
					var avail_calender = 'product-available-date-noavail';

                                        if (campsites[s].availability[a][0] == true) {
						avail_calender = 'product-available-date-avail';
					}
                                        

                                        campsitehtml = campsitehtml + "<td class='product-available-date "+avail_calender+"'>"+dasplit[2]+"/"+dasplit[1]+"</td>";
					availloop = availloop  + 1;
					if (availloop > 4) {
						campsitehtml = campsitehtml + "</tr><tr>";
						availloop = 0;
					}
				}

				campsitehtml = campsitehtml + "</tr></table>";
                                campsitehtml = campsitehtml + "</div>";
				campsitehtml = campsitehtml + "</div>";

                                campsitehtml = campsitehtml + "<div class='col-9 product-available-price-box'>";
                                campsitehtml = campsitehtml + "<div class='"+priceavail+"'>AUD: $"+campsite_price.toFixed(2)+"</div>";

				if (campsite_available == true) {
				    var key_id= 0;
				    if (campsites[s].site_type == 0) { 
                                        key_id = campsites[s].id;
			            } else {
				        key_id = campground_id; 
                                    }
                                    var buttondata = {"site_type": site_type, "campsite_id": campsites[s].id, "campground_id": campground_id, "campsite_class_id": campsites[s].type};
                                    var databutton = JSON.stringify(buttondata);
				    if (append_site == true) {
                                         campsitehtml = campsitehtml + "<button type='button' class='btn btn-success' id='bookingcampsite' data-button='"+databutton+"'   onclick='search_avail.create_booking(this)' +key_id++site_type+ >Book Now</button></div>";
				    } else {
					 campsitehtml = campsitehtml + "<button type='button' class='btn btn-secondary avail-font-bold' id='bookingcampsite' >NO MATCH</button></div>";
				    }
				} else {
				    if (append_site == true) {

				        campsitehtml = campsitehtml + "<button type='button' class='btn btn-danger avail-font-bold' id='bookingcampsite' >Not Available</button></div>";
				    } else {
					campsitehtml = campsitehtml + "<button type='button' class='btn btn-secondary avail-font-bold' id='bookingcampsite' >NO MATCH</button></div>";
				    }
				}

				campsitehtml = campsitehtml + "</div>";
                                campsitehtml = campsitehtml + "</div>";
				campsitehtml = campsitehtml + "</center></div>";
			        // campsitehtml = campsitehtml + "</div>";

				//if (search_avail.var.campers['total_people'] >= campsites[s].min_people && search_avail.var.campers['total_people']  <= campsites[s].max_people) {
				//} else {
		                //        append_site = false;
				//}


				//if (append_site == true) {
                                //     var gearType = campsites[s].gearType;
                                //     
                                //     if (tents == true && gearType.tent == false) {
                                //                append_site = false;
                                //     }

                                //     if (campervan == true && gearType.campervan == false) {
                                //                append_site = false;
                                //     }

                                //     if (campertrailer == true && gearType.caravan == false) {
                                //                append_site = false;
                                //     }
                                // }

                                // if (append_site == true) {
				//     var campsite_features = campsites[s].features;
                                //     var feats = new Set(campsite_features.map(function(x) {
                                //         return x.id;
                                //     }));

                                //     for (var x of features_checked) {
				//	   if (!feats.has(x)) {
				//		append_site = false;
				//	   }

				//     }
				//}
                                
				if (append_site == true) {
					if (campsite_available == true) {
   					     campsitehtmlbefore= campsitehtmlbefore + campsitehtml;
					} else {
                                             campsitehtmlafter= campsitehtmlafter + campsitehtml;
					}
				} else {
					 if (campsite_available == true) {
						campsitehtmlmiddlestart= campsitehtmlmiddlestart + campsitehtml;
				         } else {
                                                 campsitehtmlmiddleend= campsitehtmlmiddleend + campsitehtml;
				         }

					 //campsitehtmlmiddle= campsitehtmlmiddle + campsitehtml;
				}
		            }
			    var campsiteresultserror = "";
			    if (campsitehtmlbefore == '' && campsitehtmlafter == '' && campsitehtmlmiddlestart == '' && campsitehtmlmiddleend == '') {
				    campsiteresultserror = "<center><span style='color:red; font-weight:bold;'>Sorry, there was no results matching your filter selection.</span></center>";
		            }

            		    $("#campsite-availablity-results").html("<div class='row align-items-center'>"+campsiteresultserror+campsitehtmlbefore+campsitehtmlmiddlestart+campsitehtmlmiddleend+campsitehtmlafter+"</div>");
         	  }
            });



    },
    search_availabilty_locations: function() {



    },
    eventPath: function(evt) {
    var path = (evt.composedPath && evt.composedPath()) || evt.path,
        target = evt.target;

    if (path != null) {
        // Safari doesn't include Window, but it should.
        return (path.indexOf(window) < 0) ? path.concat(window) : path;
    }

    if (target === window) {
        return [window];
    }

    function getParents(node, memo) {
        memo = memo || [];
        var parentNode = node.parentNode;

        if (!parentNode) {
            return memo;
        }
        else {
            return getParents(parentNode, memo.concat(parentNode));
        }
    }

    return [target].concat(getParents(target), window);
    },
    bellflash: function() {
	    var current_class = $('#bell-flash').attr("class");
	    if (current_class == 'bi-bell-fill') {
		$("#bell-flash").attr("class","bi-bell");
	    } else {
		$("#bell-flash").attr("class","bi-bell-fill");
	    }
	    setTimeout("search_avail.bellflash();",1000);
    },
    init: function() {
	 var enodes = [];
         search_avail.bellflash();
         $(document).click(function(event) {
		  var closedropdowns = true;
         	  var $target = $(event.target);
		  enodes = [];
                      enodes = search_avail.eventPath(event);
		      if (typeof enodes === 'undefined') {
                             enodes = [];
	              }

	              for(let i = 0; i < enodes.length; i++) {
	                   if ('classList' in enodes[i]) {
	                       if ('value' in enodes[i].classList) { 
	                          var classlist_path = enodes[i].classList.value.split(" ");
	                          for(let c = 0; c < classlist_path.length; c++) {
	                 		if ("selection-dropdown" == classlist_path[c]) { 
	                     		closedropdowns = false;
	                 		}
                                        if ("selection-informbox" == classlist_path[c]) {
	                     		    closedropdowns = false;
   	                     	        }
	                          }
	                       }
	                   }
	              }
		      
		  if (closedropdowns == true) {
                      search_avail.close_dropdowns();        
		  }
         });
    }
}

