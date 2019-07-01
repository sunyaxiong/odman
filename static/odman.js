function apply_code() {

        let email=$('#email').val();
        console.log(email);
        $.ajax({
                 type: "POST",
                 url: "/accounts/apply_for_code/",
                 data: {
                     'email': email,
                 },
                 success: function(ret) {
                     let _data = eval("("+ret+")");
                     console.log(_data['message']);
                     $("#apply_code").attr("disabled", "disabled");
                     $("#apply_code").removeAttr("onclick");
                     $("#message").html(_data.message)
                 }
             })
         };