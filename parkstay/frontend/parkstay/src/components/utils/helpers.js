import _ from 'lodash'

export const helpers =  {
    apiError: function(resp){
        let error_str = '';
        if (resp.status === 400) {
            try {
                
                let obj = JSON.parse(resp.responseText);
                error_str = obj.non_field_errors[0].replace(/[\[\]"]/g,'');
            } catch(e) {
                error_str = resp.responseText.replace(/[\[\]"]/g,'');
            }
        }
        else if ( resp.status === 404) {
            error_str = 'The resource you are looking for does not exist.';
        }
        else{
            error_str = resp.responseText.replace(/[\[\]"]/g,'');
        }
        return error_str;
    },
    apiVueResourceError: function(resp){
        let error_str = '';
        if (resp.status === 400) {
            let text = resp.body[0];
            try {
                let obj = JSON.parse(text);
                error_str = obj.non_field_errors[0].replace(/[\[\]"]/g,'');
            } catch(e) {
                error_str = text.replace(/[\[\]"]/g,'');
            }
        }
        else if ( resp.status === 404) {
            error_str = 'The resource you are looking for does not exist.';
        }
        return error_str;
    },
    getCookie: function(name) {
        let value = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1).trim() === (name + '=')) {
                    value = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return value;
    },
    namePopover:function ($,vmDataTable) {
        vmDataTable.on('mouseover','.name_popover',function (e) {
            $(this).popover('show');
            $(this).on('mouseout',function () {
                $(this).popover('hide');
            });
        });
    },
    add_endpoint_json: function ( string, addition ) {
        let res = string.split( ".json" )
        return res[ 0 ] + '/' + addition + '.json';
      },
    dtPopover: function(value,truncate_length=30,trigger='hover'){
        let ellipsis = '...',
        truncated = _.truncate(value, {
            length: truncate_length,
            omission: ellipsis,
            separator: ' '
        }),
        result = '<span>' + truncated + '</span>',
        popTemplate = _.template('<a href="#" ' +
            'role="button" ' +
            'data-toggle="popover" ' +
            'data-trigger="'+trigger+'" ' +
            'data-placement="top auto"' +
            'data-html="true" ' +
            'data-content="<%= text %>" ' +
            '>more</a>');
        if (_.endsWith(truncated, ellipsis)) {
            result += popTemplate({
                text: value
            });
        }
        return result;
    },
    dtPopoverCellFn: function(cell){
        $(cell).find('[data-toggle="popover"]')
            .popover()
            .on('click', function (e) {
                e.preventDefault();
                return true;
            });
    }

};
