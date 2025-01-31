function voteTier(cardId, tier) {
    console.log(`Card ID: ${cardId}, Tier: ${tier}`);
    var voteUrl = `${window.location.origin}/${lang}/guide/vote`;

    $.ajax({
        url: voteUrl,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ cardId: cardId, tier: tier }),
        success: function(response) {
            if (response.html_content) {
                document.querySelector('.left').innerHTML = response.html_content;
            }
        },
        error: function(xhr) {
            console.error("Error updating vote.");
        }
    });
}
