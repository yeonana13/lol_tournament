console.log('🎉 Draft Result System 로드 시작');

class DraftResultSystem {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.socket = io();
        this.draftData = null;
        this.champions = [];
        this.bannedChampions = [];
        this.isEditMode = false;
        this.selectedPlayer = null;
        this.currentReselectPlayer = null;
        this.selectedNewChampion = null;
        
        this.initialize();
    }
    
    async initialize() {
        try {
            await this.initializeSocket();
            await this.loadDraftData();
            await this.loadChampions();
            this.renderResults();
            this.setupEventListeners();
            
            console.log('✅ 결과 시스템 초기화 완료');
        } catch (error) {
            console.error('❌ 초기화 실패:', error);
        }
    }
    
    initializeSocket() {
        return new Promise((resolve) => {
            this.socket.on('connect', () => {
                console.log('🔌 소켓 연결됨');
                this.socket.emit('join_result_session', { 
                    session_id: this.sessionId 
                });
                resolve();
            });
            
            this.socket.on('draft_data_update', (data) => {
                console.log('📊 드래프트 데이터 업데이트:', data);
                this.draftData = data;
                this.renderResults();
            });
        });
    }
    
    async loadDraftData() {
        try {
            const response = await fetch(`/api/session/${this.sessionId}/result`);
            if (response.ok) {
                this.draftData = await response.json();
                console.log('📊 드래프트 데이터 로드 완료:', this.draftData);
            } else {
                // 더미 데이터 사용
                this.loadDummyData();
            }
        } catch (error) {
            console.error('❌ 드래프트 데이터 로드 실패:', error);
            this.loadDummyData();
        }
    }
    
    loadDummyData() {
        this.draftData = {
            teams: {
                blue: {
                    TOP: { player: { display_name: '테스트유저1', avatar_url: 'https://cdn.discordapp.com/embed/avatars/1.png' }, champion: { korean_name: '아트록스', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Aatrox.png' }},
                    JUG: { player: { display_name: '테스트유저2', avatar_url: 'https://cdn.discordapp.com/embed/avatars/2.png' }, champion: { korean_name: '그레이브즈', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Graves.png' }},
                    MID: { player: { display_name: '테스트유저3', avatar_url: 'https://cdn.discordapp.com/embed/avatars/3.png' }, champion: { korean_name: '아리', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Ahri.png' }},
                    ADC: { player: { display_name: '테스트유저4', avatar_url: 'https://cdn.discordapp.com/embed/avatars/4.png' }, champion: { korean_name: '징크스', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Jinx.png' }},
                    SUP: { player: { display_name: '테스트유저5', avatar_url: 'https://cdn.discordapp.com/embed/avatars/5.png' }, champion: { korean_name: '쓰레쉬', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Thresh.png' }}
                },
                red: {
                    TOP: { player: { display_name: '테스트유저6', avatar_url: 'https://cdn.discordapp.com/embed/avatars/0.png' }, champion: { korean_name: '가렌', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Garen.png' }},
                    JUG: { player: { display_name: '테스트유저7', avatar_url: 'https://cdn.discordapp.com/embed/avatars/1.png' }, champion: { korean_name: '엘리스', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Elise.png' }},
                    MID: { player: { display_name: '테스트유저8', avatar_url: 'https://cdn.discordapp.com/embed/avatars/2.png' }, champion: { korean_name: '신드라', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Syndra.png' }},
                    ADC: { player: { display_name: '테스트유저9', avatar_url: 'https://cdn.discordapp.com/embed/avatars/3.png' }, champion: { korean_name: '베인', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Vayne.png' }},
                    SUP: { player: { display_name: '테스트유저10', avatar_url: 'https://cdn.discordapp.com/embed/avatars/4.png' }, champion: { korean_name: '레오나', image_url: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Leona.png' }}
                }
            },
            bans: {
                blue: ['야스오', '제드', '아지르', '카밀', '그웬'],
                red: ['아칼리', '리 신', '오리아나', '케이틀린', '노틸러스']
            }
        };
        this.bannedChampions = [...this.draftData.bans.blue, ...this.draftData.bans.red];
    }
    
    async loadChampions() {
        try {
            const response = await fetch(`/api/session/${this.sessionId}`);
            const data = await response.json();
            this.champions = data.champions || [];
            
            if (this.champions.length === 0) {
                this.loadDummyChampions();
            }
        } catch (error) {
            console.error('❌ 챔피언 로드 실패:', error);
            this.loadDummyChampions();
        }
    }
    
    loadDummyChampions() {
        const dummyChampions = [
            'Aatrox', 'Ahri', 'Akali', 'Alistar', 'Ammu', 'Ashe', 'Blitzcrank', 'Brand',
            'Caitlyn', 'Darius', 'Diana', 'Elise', 'Ezreal', 'Fiora', 'Garen', 'Graves',
            'Janna', 'Jax', 'Jinx', 'Katarina', 'LeeSin', 'Leona', 'Lux', 'Malphite',
            'Nasus', 'Nautilus', 'Orianna', 'Riven', 'Syndra', 'Thresh', 'Vayne', 'Yasuo', 'Zed'
        ];
        
        this.champions = dummyChampions.map(name => ({
            english_name: name,
            korean_name: name,
            image_url: `https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/${name}.png`
        }));
    }
    
    renderResults() {
        this.renderTeams();
        this.renderBans();
    }
    
    renderTeams() {
        const positions = ['TOP', 'JUG', 'MID', 'ADC', 'SUP'];
        
        // 블루팀 렌더링
        const blueTeamEl = document.getElementById('blueTeamResult');
        blueTeamEl.innerHTML = '<div class="team-header">🔵 블루팀</div>';
        
        positions.forEach(position => {
            const playerData = this.draftData.teams.blue[position];
            if (playerData) {
                const cardEl = this.createPlayerCard(position, playerData, 'blue');
                blueTeamEl.appendChild(cardEl);
            }
        });
        
        // 레드팀 렌더링
        const redTeamEl = document.getElementById('redTeamResult');
        redTeamEl.innerHTML = '<div class="team-header">🔴 레드팀</div>';
        
        positions.forEach(position => {
            const playerData = this.draftData.teams.red[position];
            if (playerData) {
                const cardEl = this.createPlayerCard(position, playerData, 'red');
                redTeamEl.appendChild(cardEl);
            }
        });
    }
    
    createPlayerCard(position, playerData, team) {
        const cardEl = document.createElement('div');
        cardEl.className = 'player-card';
        cardEl.dataset.team = team;
        cardEl.dataset.position = position;
        
        cardEl.innerHTML = `
            <div class="position-badge">${position}</div>
            <div class="player-info">
                <img src="${playerData.player.avatar_url}" alt="플레이어" class="player-avatar"
                     onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
                <div class="player-details">
                    <div class="player-name">${playerData.player.display_name}</div>
                    <div class="player-username">@${playerData.player.username || 'Player'}</div>
                </div>
            </div>
            <div class="champion-display">
                <img src="${playerData.champion.image_url}" alt="${playerData.champion.korean_name}" class="champion-icon"
                     onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
                <div class="champion-name">${playerData.champion.korean_name}</div>
            </div>
            <div class="action-buttons-group">
                <button class="swap-btn">교환</button>
                <button class="reselect-btn">재선택</button>
            </div>
        `;
        
        return cardEl;
    }
    
    renderBans() {
        const bansDisplayEl = document.getElementById('bansDisplay');
        
        bansDisplayEl.innerHTML = `
            <div class="team-bans blue-bans">
                <div class="team-bans-header">블루팀 밴</div>
                <div class="ban-champions">
                    ${this.draftData.bans.blue.map(champion => `
                       <img src="https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/${champion}.png" 
                            alt="${champion}" class="banned-champion"
                            onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
                   `).join('')}
               </div>
           </div>
           <div class="team-bans red-bans">
               <div class="team-bans-header">레드팀 밴</div>
               <div class="ban-champions">
                   ${this.draftData.bans.red.map(champion => `
                       <img src="https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/${champion}.png" 
                            alt="${champion}" class="banned-champion"
                            onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
                   `).join('')}
               </div>
           </div>
       `;
   }
   
   setupEventListeners() {
       // 교환 모드 토글
       document.getElementById('editModeBtn').addEventListener('click', () => {
           this.toggleEditMode();
       });
       
       // 재선택 버튼들
       document.addEventListener('click', (e) => {
           if (e.target.classList.contains('reselect-btn')) {
               this.handleReselectClick(e.target);
           }
           if (e.target.classList.contains('swap-btn')) {
               this.handleSwapClick(e.target);
           }
       });
       
       // 모달 이벤트들
       this.setupModalEvents();
       
       // 확정 버튼
       document.getElementById('confirmBtn').addEventListener('click', () => {
           this.confirmResults();
       });
       
       // 미세 조정 완료 버튼
       document.getElementById('restartBtn').addEventListener('click', () => {
           this.saveAdjustments();
       });
   }
   
   toggleEditMode() {
       this.isEditMode = !this.isEditMode;
       const btn = document.getElementById('editModeBtn');
       
       document.body.classList.toggle('swap-mode', this.isEditMode);
       
       if (this.isEditMode) {
           btn.textContent = '❌ 교환 모드 종료';
           btn.style.background = 'linear-gradient(135deg, #CD5334 0%, #F0464E 100%)';
           btn.style.color = 'white';
       } else {
           btn.textContent = '🔄 챔피언 교환 모드';
           btn.style.background = 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)';
           btn.style.color = '#000000';
           this.clearSelection();
       }
   }
   
   handleReselectClick(btn) {
       const playerCard = btn.closest('.player-card');
       const playerName = playerCard.querySelector('.player-name').textContent;
       const position = playerCard.querySelector('.position-badge').textContent;
       
       this.currentReselectPlayer = playerCard;
       this.selectedNewChampion = null;
       
       document.getElementById('modalPlayerInfo').textContent = 
           `${playerName} (${position}) - 새로운 챔피언을 선택하세요`;
       
       this.showReselectModal();
   }
   
   handleSwapClick(btn) {
       const playerCard = btn.closest('.player-card');
       
       if (this.selectedPlayer === null) {
           this.selectedPlayer = playerCard;
           playerCard.classList.add('selected');
           
           // 같은 팀의 다른 플레이어들을 교환 가능으로 표시
           const team = playerCard.dataset.team;
           const teamCards = document.querySelectorAll(`[data-team="${team}"] .player-card`);
           
           teamCards.forEach(card => {
               if (card !== playerCard) {
                   card.classList.add('swappable');
               }
           });
           
           btn.textContent = '취소';
           btn.style.background = 'linear-gradient(135deg, #CD5334 0%, #F0464E 100%)';
           btn.style.color = 'white';
       } else {
           this.clearSelection();
       }
   }
   
   clearSelection() {
       document.querySelectorAll('.player-card').forEach(card => {
           card.classList.remove('selected', 'swappable');
       });
       
       document.querySelectorAll('.swap-btn').forEach(btn => {
           btn.textContent = '교환';
           btn.style.background = 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)';
           btn.style.color = '#000000';
       });
       
       this.selectedPlayer = null;
   }
   
   showReselectModal() {
       const modal = document.getElementById('reselectModal');
       this.renderModalChampions('');
       modal.classList.add('active');
   }
   
   renderModalChampions(searchTerm = '') {
       const grid = document.getElementById('modalChampionGrid');
       const currentPicks = this.getCurrentPicks();
       
       grid.innerHTML = '';
       
       const filteredChampions = this.champions.filter(champ => 
           champ.english_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           champ.korean_name.includes(searchTerm)
       );
       
       filteredChampions.forEach(champion => {
           const item = document.createElement('div');
           item.className = 'modal-champion-item';
           item.dataset.championName = champion.english_name;
           item.dataset.championKorean = champion.korean_name;
           
           if (this.bannedChampions.includes(champion.korean_name)) {
               item.classList.add('banned');
           } else if (currentPicks.includes(champion.korean_name)) {
               item.classList.add('picked');
           }
           
           item.innerHTML = `<img src="${champion.image_url}" alt="${champion.korean_name}"
                                  onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">`;
           
           if (!item.classList.contains('banned') && !item.classList.contains('picked')) {
               item.addEventListener('click', () => {
                   document.querySelectorAll('.modal-champion-item').forEach(el => {
                       el.classList.remove('selected');
                   });
                   
                   item.classList.add('selected');
                   this.selectedNewChampion = champion;
                   
                   document.getElementById('modalConfirm').disabled = false;
               });
           }
           
           grid.appendChild(item);
       });
   }
   
   getCurrentPicks() {
       const picks = [];
       document.querySelectorAll('.champion-name').forEach(nameEl => {
           picks.push(nameEl.textContent);
       });
       return picks;
   }
   
   setupModalEvents() {
       // 모달 검색
       document.getElementById('modalSearch').addEventListener('input', (e) => {
           this.renderModalChampions(e.target.value);
       });
       
       // 모달 확인
       document.getElementById('modalConfirm').addEventListener('click', () => {
           this.confirmReselection();
       });
       
       // 모달 취소
       document.getElementById('modalCancel').addEventListener('click', () => {
           this.closeReselectModal();
       });
       
       // 모달 외부 클릭
       document.getElementById('reselectModal').addEventListener('click', (e) => {
           if (e.target.id === 'reselectModal') {
               this.closeReselectModal();
           }
       });
   }
   
   confirmReselection() {
       if (this.selectedNewChampion && this.currentReselectPlayer) {
           const championDisplay = this.currentReselectPlayer.querySelector('.champion-display');
           
           championDisplay.innerHTML = `
               <img src="${this.selectedNewChampion.image_url}" alt="${this.selectedNewChampion.korean_name}" class="champion-icon"
                    onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
               <div class="champion-name">${this.selectedNewChampion.korean_name}</div>
           `;
           
           // 변경 효과
           championDisplay.style.transform = 'scale(1.2)';
           championDisplay.style.boxShadow = '0 0 30px rgba(155, 89, 182, 0.8)';
           
           setTimeout(() => {
               championDisplay.style.transform = 'scale(1)';
               championDisplay.style.boxShadow = '0 0 15px rgba(0, 255, 136, 0.4)';
           }, 500);
           
           // 데이터 업데이트
           const team = this.currentReselectPlayer.dataset.team;
           const position = this.currentReselectPlayer.dataset.position;
           this.draftData.teams[team][position].champion = this.selectedNewChampion;
           
           this.closeReselectModal();
           console.log('✅ 챔피언 재선택 완료:', this.selectedNewChampion.korean_name);
       }
   }
   
   closeReselectModal() {
       document.getElementById('reselectModal').classList.remove('active');
       this.currentReselectPlayer = null;
       this.selectedNewChampion = null;
       document.getElementById('modalSearch').value = '';
       document.getElementById('modalConfirm').disabled = true;
   }
   
   confirmResults() {
       if (confirm('정말로 이 결과를 확정하시겠습니까?\n디스코드로 결과가 전송됩니다.')) {
           const btn = document.getElementById('confirmBtn');
           btn.textContent = '전송 중...';
           btn.disabled = true;
           
           // 서버로 최종 결과 전송
           this.socket.emit('confirm_draft_results', {
               session_id: this.sessionId,
               final_data: this.draftData
           });
           
           setTimeout(() => {
               alert('🎉 결과가 디스코드로 전송되었습니다!');
               btn.textContent = '✅ 전송 완료';
           }, 2000);
       }
   }
   
   saveAdjustments() {
       // 수정사항 저장
       this.socket.emit('save_draft_adjustments', {
           session_id: this.sessionId,
           adjustments: this.draftData
       });
       
       alert('✅ 수정사항이 저장되었습니다!\n언제든 다시 수정할 수 있습니다.');
   }
}

// 페이지 로드 시 시스템 초기화
document.addEventListener('DOMContentLoaded', function() {
   const sessionId = document.body.dataset.sessionId;
   
   if (sessionId) {
       console.log('🚀 DraftResultSystem 시작:', sessionId);
       window.draftResultSystem = new DraftResultSystem(sessionId);
   } else {
       console.error('❌ 세션 ID를 찾을 수 없습니다.');
   }
});
