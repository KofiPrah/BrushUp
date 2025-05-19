// Simple, direct reaction button handler
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing reaction buttons with direct handlers');
    
    // Find all reaction buttons and attach click handlers
    document.querySelectorAll('[data-reaction-critique-id]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const critiqueId = this.getAttribute('data-reaction-critique-id');
            const reactionType = this.getAttribute('data-reaction-type');
            
            console.log(`Clicked reaction: ${reactionType} for critique ${critiqueId}`);
            
            // Visual feedback
            this.classList.add('clicked');
            setTimeout(() => this.classList.remove('clicked'), 300);
            
            // Get the CSRF token from the page
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Create a form to submit the reaction (this is more reliable than fetch)
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/critiques/${critiqueId}/react/ajax/`;
            form.style.display = 'none';
            
            // Add CSRF token
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            // Add reaction type
            const reactionInput = document.createElement('input');
            reactionInput.type = 'hidden';
            reactionInput.name = 'reaction_type';
            reactionInput.value = reactionType;
            form.appendChild(reactionInput);
            
            // Add AJAX header
            const ajaxInput = document.createElement('input');
            ajaxInput.type = 'hidden';
            ajaxInput.name = 'X-Requested-With';
            ajaxInput.value = 'XMLHttpRequest';
            form.appendChild(ajaxInput);
            
            // Submit the form
            document.body.appendChild(form);
            
            // Use fetch instead of form submission for better user experience
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: new URLSearchParams({
                    'reaction_type': reactionType
                })
            })
            .then(response => {
                if (response.ok) {
                    console.log('Reaction processed successfully');
                    
                    // Toggle button state
                    if (reactionType === 'HELPFUL') {
                        this.classList.toggle('btn-success');
                        this.classList.toggle('btn-outline-success');
                    } else if (reactionType === 'INSPIRING') {
                        this.classList.toggle('btn-primary');
                        this.classList.toggle('btn-outline-primary');
                    } else if (reactionType === 'DETAILED') {
                        this.classList.toggle('btn-info');
                        this.classList.toggle('btn-outline-info');
                    }
                    
                    // Attempt to update the count
                    try {
                        const countBadge = this.querySelector(`.${reactionType.toLowerCase()}-count`);
                        if (countBadge) {
                            const currentCount = parseInt(countBadge.textContent);
                            if (this.classList.contains('btn-outline-success') || 
                                this.classList.contains('btn-outline-primary') || 
                                this.classList.contains('btn-outline-info')) {
                                // Reaction removed
                                countBadge.textContent = Math.max(0, currentCount - 1);
                            } else {
                                // Reaction added
                                countBadge.textContent = currentCount + 1;
                            }
                        }
                    } catch (err) {
                        console.error('Error updating count:', err);
                    }
                } else {
                    console.error('Error processing reaction:', response.status);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
            
            // Remove the form
            setTimeout(() => {
                form.remove();
            }, 100);
        });
    });
});