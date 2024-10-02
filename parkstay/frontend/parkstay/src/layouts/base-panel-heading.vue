<template lang="html">
    <div class="panel-heading clearfix">
        <h3 class="panel-title pull-left" style="padding-top: 7.5px;">{{ title }}</h3>
        <div class="btn-group pull-right">
            <slot style="justify-content: space-around;"/>
        </div>
    </div>
</template>

<script>
export default {
    name: "BasePanelHeading",
    props: {
        title: {
            type: String,
        },
    },
}
</script>