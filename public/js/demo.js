function showFeedback(form, message, state = '') {
    const feedback = form.querySelector('[data-feedback]');
    feedback.textContent = message;
    feedback.dataset.state = state;
}

function clearErrors(form) {
    form.querySelectorAll('[data-field-error]').forEach(element => element.replaceChildren());
    form.querySelectorAll('[aria-invalid]').forEach(element => element.setAttribute('aria-invalid', 'false'));
}

function showErrors(form, fields) {
    form.querySelectorAll('[data-field-error]').forEach(element => {
        const field = element.dataset.fieldError;
        const messages = fields[field];
        if (!Array.isArray(messages)) {
            return;
        }

        messages.forEach(message => {
            const paragraph = document.createElement('p');
            paragraph.textContent = message;
            element.append(paragraph);
        });
        form.elements.namedItem(field)?.setAttribute('aria-invalid', 'true');
    });
    form.querySelector('[aria-invalid="true"]')?.focus();
}

if (window.fetch && window.FormData && window.AbortController) {
    document.querySelectorAll('form[data-demo]').forEach(form => {
        const responseCode = form.querySelector('[data-response]');
        const exampleResponse = responseCode?.textContent;
        form.noValidate = true;

        form.addEventListener('reset', () => {
            clearErrors(form);
            showFeedback(form, 'Ready for another try.');
            if (responseCode) {
                responseCode.textContent = exampleResponse;
                form.querySelector('[data-response-title]').textContent = 'Example response';
                form.querySelector('[data-response-status]').textContent = 'Ready';
                delete form.querySelector('[data-response-status]').dataset.state;
            }
        });

        form.addEventListener('submit', async event => {
            event.preventDefault();
            if (form.getAttribute('aria-busy') === 'true') {
                return;
            }

            const body = new FormData(form);
            const buttons = [...form.querySelectorAll('button')].filter(button => !button.disabled);
            const controller = new AbortController();
            const timeout = window.setTimeout(() => controller.abort(), 15000);
            buttons.forEach(button => button.disabled = true);
            form.setAttribute('aria-busy', 'true');
            clearErrors(form);
            showFeedback(form, 'Sending your request…');
            if (responseCode) {
                responseCode.textContent = 'Waiting for the server…';
                form.querySelector('[data-response-status]').textContent = 'Sending…';
                delete form.querySelector('[data-response-status]').dataset.state;
            }

            try {
                const response = await fetch(form.action, {
                    method: form.method,
                    body,
                    headers: { Accept: 'application/json' },
                    credentials: 'same-origin',
                    signal: controller.signal,
                });

                if (responseCode) {
                    const status = form.querySelector('[data-response-status]');
                    form.querySelector('[data-response-title]').textContent = 'Server response';
                    status.textContent = `HTTP ${response.status}`;
                    status.dataset.state = response.ok ? 'success' : 'error';
                }

                if (!response.headers.get('Content-Type')?.includes('application/json')) {
                    if (responseCode) {
                        responseCode.textContent = 'The server did not return JSON.';
                    }
                    showFeedback(form, response.status === 400
                        ? 'Request refused. Reload this page for a fresh form token, then try again.'
                        : `Unexpected response (HTTP ${response.status}). Please try again.`, 'error');
                    return;
                }

                const result = await response.json();
                if (responseCode) {
                    responseCode.textContent = JSON.stringify(result, null, 2);
                }

                if (!response.ok) {
                    showErrors(form, result.fields ?? {});
                    showFeedback(form, result.fields
                        ? 'Please check the highlighted fields and try again.'
                        : 'The request failed. Please try again.', 'error');
                    return;
                }

                showFeedback(form, form.dataset.demo === 'contact'
                    ? result.data.message
                    : 'Response received. Try another name.', 'success');
            } catch (error) {
                if (responseCode) {
                    responseCode.textContent = 'No readable response received.';
                    form.querySelector('[data-response-status]').textContent = 'Request failed';
                    form.querySelector('[data-response-status]').dataset.state = 'error';
                }
                showFeedback(form, error.name === 'AbortError'
                    ? 'The request timed out. Please try again.'
                    : 'Could not complete the request. Check your connection and try again.', 'error');
            } finally {
                window.clearTimeout(timeout);
                buttons.forEach(button => button.disabled = false);
                form.setAttribute('aria-busy', 'false');
            }
        });
    });
}

document.querySelector('[data-start-fresh]')?.addEventListener('click', () => {
    document.querySelector('#remove-demo').open = true;
});

document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
        const code = button.closest('.command-block').querySelector('code');
        try {
            await navigator.clipboard.writeText(code.textContent);
            button.textContent = 'Copied';
        } catch {
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(code);
            selection.removeAllRanges();
            selection.addRange(range);
            button.textContent = 'Selected — press Ctrl/Cmd+C';
        }
    });
});
