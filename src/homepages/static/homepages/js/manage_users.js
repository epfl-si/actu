document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById('ajaxSearchInput');
    const dropdown = document.getElementById('searchResultsDropdown');
    const addBtn = document.getElementById('add-btn');
    const inputSpinner = document.getElementById('input-spinner');

    const addForm = document.getElementById('addForm');
    const addSciperInput = document.getElementById('addSciper');

    const transAdd = searchInput.dataset.transAdd;
    const transNoResults = searchInput.dataset.transNoResults;

    let debounceTimer;
    let selectedSciper = null;

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();

        addBtn.style.display = 'none';
        selectedSciper = null;
        dropdown.style.display = 'none';
        inputSpinner.style.display = 'none';

        clearTimeout(debounceTimer);

        if (query.length < 3) return;

        debounceTimer = setTimeout(() => {
            inputSpinner.style.display = 'block';

            fetch(`?q=${encodeURIComponent(query)}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                inputSpinner.style.display = 'none';
                dropdown.innerHTML = '';

                if (data.results && data.results.length > 0) {
                    data.results.forEach(user => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item';
                        li.textContent = user.text;

                        li.addEventListener('click', () => {
                            searchInput.value = user.text;
                            selectedSciper = user.sciper;

                            dropdown.style.display = 'none';
                            addBtn.style.display = 'block';
                            addBtn.textContent = `${transAdd} ${user.text}`;
                        });

                        dropdown.appendChild(li);
                    });
                    dropdown.style.display = 'block';
                } else {
                    const li = document.createElement('li');
                    li.className = 'list-group-item text-muted';
                    li.style.cursor = 'default';

                    li.innerHTML = `<i>${transNoResults}</i>`;

                    dropdown.appendChild(li);
                    dropdown.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Erreur AJAX:', error);
                inputSpinner.style.display = 'none';
            });
        }, 800);
    });

    document.addEventListener('click', function(e) {
        if (e.target !== searchInput) {
            dropdown.style.display = 'none';
        }
    });

    addBtn.addEventListener('click', function() {
        if (!selectedSciper) return;

        addSciperInput.value = selectedSciper;
        addForm.submit();
    });
});
