document.addEventListener('DOMContentLoaded', function() {
    const searchBarContainer = document.querySelector('.searchbar-container');

    searchBarContainer.addEventListener('click', function() {
        searchBarContainer.classList.add('active');
    });

    const searchInput = document.querySelector('input[name="query"]');
    const suggestionsBox = document.getElementById('suggestions-box');
    const notificationsList = document.querySelector('.notifications-container');

    if (searchInput && suggestionsBox) {
        searchInput.addEventListener('input', function () {
        const query = this.value.trim();
        if (query.length > 0) {
            // show suggestions immediately (so user sees loading state)
            suggestionsBox.classList.add('visible');
            // hide notifications if open
            notificationsList?.classList.remove('visible');

            // then fetch and populate suggestions
            fetch(`/search-suggestions/?query=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                suggestionsBox.innerHTML = '';
                console.log('Response Data', data);

                if (data.role === 'admin' && data.user_count > 0) {
                createCategoryHeader('Users', data.user_count);
                const suggestionList = createSuggestionList();
                data.users.forEach(user => suggestionList.append(createSuggestionItem('user', user)));
                suggestionsBox.append(suggestionList);
                }

                if (data.documents?.count > 0) {
                createCategoryHeader(data.role === 'admin' ? 'Documents' : 'My Documents', data.documents.count);
                const suggestionList = createSuggestionList();
                data.documents.results.forEach(result => suggestionList.append(createSuggestionItem('document', result)));
                suggestionsBox.append(suggestionList);
                }
            })
            .catch(err => {
                console.error('Suggestions fetch failed', err);
                // optionally show an error or empty state in suggestionsBox
            });
        } else {
            suggestionsBox.classList.remove('visible');
        }
        });
    }

    // click outside -> remove 'active'
    document.addEventListener('click', function(e) {
        // check if the click target is NOT inside the searchBarContainer
        if (!searchBarContainer.contains(e.target)) {
            searchBarContainer.classList.remove('active');
        }

        if (suggestionsBox.classList.contains('visible')) {
            suggestionsBox.classList.remove('visible')
        }
    });


    function createCategoryHeader(category, itemCount) {
        const header = document.createElement('div');
        header.classList.add('suggestions-header');

        header.innerHTML = `
            <div style="display:flex; align-items:center; justify-content: space-between;">
                <h3>${category} <span class="suggestion-count">${itemCount}</span></h3>
                <i class="fa-solid fa-angle-right"></i>
            </div>
        `;
        suggestionsBox.append(header);
    }

    function createSuggestionList() {
        const suggestionList = document.createElement('div');
        suggestionList.classList.add('suggestions-list');
        return suggestionList;
    }

    function createSuggestionItem(type, item, link) {
        const suggestionDiv = document.createElement('div');
        suggestionDiv.classList.add('suggestion-item');

        let itemContent = '';

        if (type === 'user') {
            itemContent = `
                <a href="${item.link}/${item.id}">
                    <div class="details">
                        <div class="suggestion-item-image">
                            <img src=${item.profile_picture}></img>
                        </div>
                        <div class="column">
                            <strong>${item.full_name}</strong>
                            <span class="role">${item.role}</span>
                        </div>
                    </div>
                </a>
            `;
        } else if (type === 'document') {
            itemContent = `
                <a href="/documents/${item.link}/${item.id}">
                    <div class="details">
                        <div class="suggestion-item-image">
                            <i class="fa-solid fa-file"></i>
                        </div>
                        <div class="column">
                            <strong>${item.display}</strong>
                            <span class="doc-type">${item.model}</span>
                        </div>
                    </div>
                </a>
            `;
        }

        suggestionDiv.innerHTML = itemContent;
        return suggestionDiv;
    }
});
