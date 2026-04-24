import Swal from 'sweetalert2';

// Inject custom CSS for SweetAlert2 to match design images
if (typeof document !== 'undefined') {
    const style = document.createElement('style');
    style.innerHTML = `
        .swal2-popup {
            border-radius: 24px !important;
            padding: 2rem !important;
            font-family: 'Poppins_400Regular', sans-serif !important;
        }
        .swal2-title {
            font-family: 'Poppins_700Bold', sans-serif !important;
            color: #0f172a !important;
            font-size: 24px !important;
            padding-top: 0 !important;
            margin-bottom: 0.5rem !important;
        }
        .swal2-html-container {
            font-family: 'Poppins_400Regular', sans-serif !important;
            color: #64748b !important;
            font-size: 16px !important;
            margin: 0 !important;
            text-align: left !important;
        }
        /* Success Icon Styling */
        .swal2-icon.swal2-success {
            border-color: #e2fbe5 !important;
            background-color: #e2fbe5 !important;
        }
        .swal2-icon.swal2-success [class^=swal2-success-line] {
            background-color: #16a34a !important;
        }
        .swal2-icon.swal2-success .swal2-success-ring {
            border: .25em solid rgba(22, 163, 74, .2) !important;
        }

        /* Button Styling */
        .swal2-actions {
            margin-top: 2rem !important;
            width: 100% !important;
            justify-content: flex-end !important;
            gap: 12px !important;
        }
        .swal2-styled.swal2-confirm.swal2-blue-button {
            background-color: #3b82f6 !important;
            border: 2px solid #000000 !important;
            border-radius: 16px !important;
            padding: 12px 32px !important;
            font-family: 'Poppins_700Bold', sans-serif !important;
            font-size: 16px !important;
            box-shadow: none !important;
            min-width: 120px !important;
        }
        .swal2-styled.swal2-confirm.swal2-red-button {
            background-color: #ef4444 !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            font-family: 'Poppins_700Bold', sans-serif !important;
            font-size: 16px !important;
            margin: 0 !important;
            flex: 1 !important;
        }
        .swal2-styled.swal2-cancel.swal2-gray-button {
            background-color: #f1f5f9 !important;
            color: #64748b !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            font-family: 'Poppins_700Bold', sans-serif !important;
            font-size: 16px !important;
            margin: 0 !important;
            flex: 1 !important;
        }
        /* Success specific button center alignment */
        .swal2-success-actions {
            justify-content: center !important;
        }
    `;
    document.head.appendChild(style);
}

const commonOptions = {
    buttonsStyling: false,
    showCloseButton: false,
    allowOutsideClick: false,
};

export const dialogs = {
    /**
     * Show a simple alert modal (used for validation, etc.)
     */
    alert: (title, text, icon = 'info') => {
        return Swal.fire({
            ...commonOptions,
            title,
            text,
            icon,
            confirmButtonText: 'OK',
            customClass: {
                popup: 'swal2-popup',
                title: 'swal2-title',
                confirmButton: 'swal2-styled swal2-confirm swal2-blue-button'
            }
        });
    },

    /**
     * Show a success modal (Matches Image 1)
     */
    success: (title, text) => {
        return Swal.fire({
            ...commonOptions,
            title: title || 'Success!',
            text: text,
            icon: 'success',
            confirmButtonText: 'Done',
            customClass: {
                popup: 'swal2-popup',
                title: 'swal2-title',
                confirmButton: 'swal2-styled swal2-confirm swal2-blue-button',
                actions: 'swal2-actions swal2-success-actions'
            },
            showClass: {
                popup: 'animate__animated animate__fadeInUp animate__faster'
            }
        });
    },

    /**
     * Show an error modal
     */
    error: (title, text) => {
        return Swal.fire({
            ...commonOptions,
            title: title || 'Error!',
            text: text,
            icon: 'error',
            confirmButtonText: 'OK',
            customClass: {
                popup: 'swal2-popup',
                title: 'swal2-title',
                confirmButton: 'swal2-styled swal2-confirm swal2-red-button'
            }
        });
    },

    /**
     * Show a confirmation modal (Matches Image 2)
     */
    confirm: (title, text, confirmButtonText = 'Delete', cancelButtonText = 'Cancel') => {
        // Handle multiline text for "item name" effect in image
        const html = text ? `<div>${text}</div>` : '';

        return Swal.fire({
            ...commonOptions,
            title: title || 'Are you sure?',
            html: html,
            showCancelButton: true,
            confirmButtonText: confirmButtonText,
            cancelButtonText: cancelButtonText,
            reverseButtons: true,
            customClass: {
                popup: 'swal2-popup',
                title: 'swal2-title',
                confirmButton: 'swal2-styled swal2-confirm swal2-red-button',
                cancelButton: 'swal2-styled swal2-cancel swal2-gray-button',
                actions: 'swal2-actions'
            }
        });
    },

    /**
     * Show a temporary toast notification
     */
    toast: (title, icon = 'success') => {
        Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
        }).fire({
            icon: icon,
            title: title
        });
    }
};

export default dialogs;
