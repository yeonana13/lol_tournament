class OAuthModal {
    constructor() {
        this.modal = null;
        this.popup = null;
        this.checkInterval = null;
    }

    show(redirectUrl) {
        this.createModal();
        this.openPopup(redirectUrl);
        this.startChecking();
    }

    createModal() {
        // 기존 모달 제거
        const existingModal = document.querySelector('.oauth-modal');
        if (existingModal) {
            existingModal.remove();
        }

        this.modal = document.createElement('div');
        this.modal.className = 'oauth-modal';
        this.modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>🎮 Discord 로그인</h2>
                    <button class="close-btn" onclick="oauthModal.close()">✕</button>
                </div>
                <div class="modal-body">
                    <div class="login-status">
                        <div class="loading-spinner"></div>
                        <p>Discord 로그인 팝업이 열렸습니다.</p>
                        <p class="sub-text">팝업이 차단되었다면 아래 버튼을 클릭하세요.</p>
                    </div>
                    <div class="modal-actions">
                        <button class="btn-popup" onclick="oauthModal.reopenPopup()">
                            팝업 다시 열기
                        </button>
                        <button class="btn-direct" onclick="window.location.href='/auth/discord'">
                            직접 이동하기
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);
    }

    openPopup(url) {
        const width = 500;
        const height = 700;
        const left = (window.innerWidth - width) / 2;
        const top = (window.innerHeight - height) / 2;

        this.popup = window.open(
            url,
            'discord_oauth',
            `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
        );

        if (!this.popup) {
            this.showPopupBlocked();
        }
    }

    showPopupBlocked() {
        const statusElement = this.modal.querySelector('.login-status p');
        statusElement.textContent = '팝업이 차단되었습니다. 아래 버튼을 이용해주세요.';
        statusElement.style.color = '#e63946';
    }

    startChecking() {
        this.checkInterval = setInterval(() => {
            if (this.popup && this.popup.closed) {
                this.handlePopupClosed();
            }
        }, 1000);
    }

    handlePopupClosed() {
        clearInterval(this.checkInterval);
        
        // 로그인 성공 여부 확인
        fetch('/api/user')
            .then(response => response.json())
            .then(data => {
                if (data.id) {
                    // 로그인 성공
                    this.showSuccess(data.final_name || data.display_name);
                    setTimeout(() => {
                        this.close();
                        window.location.reload(); // 페이지 새로고침으로 로그인 상태 반영
                    }, 2000);
                } else {
                    // 로그인 실패 또는 취소
                    this.showCancelled();
                }
            })
            .catch(error => {
                console.error('로그인 상태 확인 실패:', error);
                this.showError();
            });
    }

    showSuccess(userName) {
        const modalBody = this.modal.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="success-message">
                <div class="success-icon">✅</div>
                <h3>로그인 성공!</h3>
                <p>환영합니다, <strong>${userName}</strong>님!</p>
                <p class="sub-text">페이지를 새로고침하는 중...</p>
            </div>
        `;
    }

    showCancelled() {
        const modalBody = this.modal.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="cancelled-message">
                <div class="cancelled-icon">❌</div>
                <h3>로그인 취소</h3>
                <p>로그인이 취소되었습니다.</p>
                <button class="btn-retry" onclick="oauthModal.reopenPopup()">다시 시도</button>
            </div>
        `;
    }

    showError() {
        const modalBody = this.modal.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="error-message">
                <div class="error-icon">⚠️</div>
                <h3>오류 발생</h3>
                <p>로그인 중 오류가 발생했습니다.</p>
                <button class="btn-retry" onclick="oauthModal.reopenPopup()">다시 시도</button>
            </div>
        `;
    }

    reopenPopup() {
        if (this.popup) {
            this.popup.close();
        }
        this.openPopup('/auth/discord');
        this.startChecking();
        
        // 모달 내용 초기화
        const modalBody = this.modal.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="login-status">
                <div class="loading-spinner"></div>
                <p>Discord 로그인 팝업이 열렸습니다.</p>
                <p class="sub-text">팝업이 차단되었다면 아래 버튼을 클릭하세요.</p>
            </div>
            <div class="modal-actions">
                <button class="btn-popup" onclick="oauthModal.reopenPopup()">
                    팝업 다시 열기
                </button>
                <button class="btn-direct" onclick="window.location.href='/auth/discord'">
                    직접 이동하기
                </button>
            </div>
        `;
    }

    close() {
        if (this.popup) {
            this.popup.close();
        }
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
        if (this.modal) {
            this.modal.remove();
        }
    }
}

// 전역 객체 생성
const oauthModal = new OAuthModal();

// Discord 로그인 함수 (전역)
function loginWithDiscord() {
    oauthModal.show('/auth/discord');
}
