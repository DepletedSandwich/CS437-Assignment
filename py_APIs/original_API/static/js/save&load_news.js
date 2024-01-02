document.getElementById("load_form").addEventListener("submit", function(event) {
	event.preventDefault();

	const selectedFile = document.getElementById("file_select").value;

	fetch('/load_news', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		credentials: 'include',
		body: JSON.stringify({ select_option: selectedFile })
	})
	.then(response => response.json())
	.then(data => {
		updateContent(data);
	})
	.catch(error => console.error('Error:', error));
});
function updateContent(data) {
	const saveSuccessElement = document.getElementById("save_success");
	if (saveSuccessElement) {
		saveSuccessElement.style.display = "none";
	}
	const contentDiv = document.getElementById("cards_fill");
	contentDiv.innerHTML = '';          
	if (Array.isArray(data)) {
		data.forEach(item => {
			let card_obj = ''
			card_obj += '<div class="card"> <div class= "card-body">'
			card_obj += `<h5 class="card-title">${item.title}</h5>`
			card_obj += `<span class="badge bg-secondary agency-badge">${item.agency}</span>`
			card_obj += `<p class="card-text"><small class="text-muted">${item.publish_date}</small></p>`
			card_obj += '</div> </div>'
			contentDiv.innerHTML += card_obj; 
        	});
	} else {
        	contentDiv.innerHTML = `<p>Invalid Content</p>`;
        }
};
