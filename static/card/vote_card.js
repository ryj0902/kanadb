function voteTier(cardId, category, tier) {
    console.log(`Card ID: ${cardId}, Category: ${category}, Tier: ${tier}`);
    var voteUrl = `${window.location.origin}/${lang}/guide/vote`;

    $.ajax({
        url: voteUrl,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ cardId: cardId, category: category, tier: tier }),
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