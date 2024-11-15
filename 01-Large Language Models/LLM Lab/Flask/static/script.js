$(function () {
    $("#eval-form").submit(async e => {
        e.preventDefault();

        var candidate = $("#candidate").val().trim();
        var job = $("#job").val().trim();

        if (candidate.length > 0 && job.length > 0) {
            var data = new FormData();
            data.append("candidate", candidate);
            data.append("job", job);

            var scoreElement = $("#score");
            var explanationElement = $("#explanation");
            var overlayElement = $("#overlay");

            scoreElement.text("");
            explanationElement.text("");
            overlayElement.show();

            try {
                // Post the candidate and job descriptions to the server
                var response = await fetch("/eval", {
                    method: "post",
                    body: data
                });

                overlayElement.hide();
                var reader = response.body.getReader();
                var decoder = new TextDecoder("utf-8");                

                // Stream the output
                while (true) {
                    var { done, value } = await reader.read();
                    if (done)
                        break;
        
                    var chunk = decoder.decode(value, { stream: true });
                    
                    if (chunk.startsWith("[[[") && chunk.endsWith("]]]")) {
                        // Show the score
                        var score = chunk.slice(3, chunk.length - 3);
                        scoreElement.text(score);
                    }
                    else {
                        // Show the next chunk of the explanation
                        var html = explanationElement.html();
                        explanationElement.html(html + chunk.replaceAll("\n", "<br>"));
                    }
                }
            }
            catch(error) {
                alert(error);
            }
            finally {
                overlayElement.hide();
            }
        }
    });
});