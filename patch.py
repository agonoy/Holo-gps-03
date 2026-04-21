import sys

with open('src/App.tsx', 'r') as f:
    content = f.read()

# 1. Remove the floating direction and heading panels from their old locations
old_panels_start = '''          <div className="absolute top-6 left-16 z-[1000] flex flex-col gap-2 pointer-events-none">'''
old_panels_end = '''                  </button>
                </div>
              </motion.div>
            )}
          </div>'''

if old_panels_start in content and old_panels_end in content:
    start_idx = content.find(old_panels_start)
    end_idx = content.find(old_panels_end) + len(old_panels_end)
    # Delete the old block
    content = content[:start_idx] + content[end_idx:]
else:
    print("Could not find old panels block to remove!")
    sys.exit(1)

# 2. Insert the sub-header right after the main header
header_end = '''        </div>
      </header>'''

new_subheader = '''        </div>
      </header>

      {/* Sub Header for Floating Panels */}
      {(showDirectionPanel || showHeadingPanel) && (
        <div className="bg-brand-surface border-b border-border z-[100] flex flex-wrap items-center justify-between px-4 py-2 shrink-0 empty:hidden gap-4">
          {/* Direction to Base */}
          {showDirectionPanel && activeRide && currentPath.length > 0 && (
            <div className="flex flex-1 items-center justify-between gap-4 bg-panel border border-border px-3 py-1.5 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-[8px] font-black uppercase text-accent tracking-tighter">Direction to Base</span>
                <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-green-500/10 p-1.5 rounded-full">
                  <ArrowUp 
                    className="text-green-500 transition-transform duration-500" 
                    size={16} 
                    style={{ 
                      transform: `rotate(${course !== null ? (getBearing(currentPath[currentPath.length-1].lat, currentPath[currentPath.length-1].lng, currentPath[0].lat, currentPath[0].lng) - (mapRotationMode === 'heading' ? course : 0)) : 0}deg)` 
                    }} 
                  />
                </div>
                <div className="flex flex-col">
                  <span className="text-[12px] font-black leading-none">{formatMileage(getDirectDist())} mi</span>
                  <span className="text-[7px] font-bold text-text-dim uppercase">Direct Line</span>
                </div>
                <button 
                  onClick={() => setShowDirectionPanel(false)}
                  className="p-0.5 ml-2 hover:bg-white/10 rounded-full transition-colors"
                >
                  <X size={12} className="text-text-dim" />
                </button>
              </div>
            </div>
          )}

          {/* Compass / Heading */}
          {showHeadingPanel && (
            <div className="flex flex-1 items-center justify-end gap-3 bg-panel border border-border px-3 py-1.5 rounded-lg transition-all">
              <div className="flex flex-col items-end">
                <span className="text-[11px] font-black tracking-widest text-accent uppercase">
                  {displayedHeading !== null ? `${getCardinalDirection(displayedHeading)} ${Math.round(displayedHeading)}°` : '---°'}
                </span>
                <span className="text-[8px] font-bold text-text-dim uppercase leading-none">
                  {displayedHeading !== null ? getFullDirection(displayedHeading) : 'Compass Off'}
                </span>
              </div>
              <div 
                className="relative h-8 w-8 rounded-full border border-border/50 flex items-center justify-center transition-transform duration-500 shrink-0"
                style={{ transform: `rotate(${mapRotationMode === 'heading' && course !== null ? -course : 0}deg)` }}
              >
                <span className="absolute top-0.5 text-[7px] font-black text-red-500">N</span>
                <div className="w-px h-full bg-border/30 absolute" />
                <div className="w-full h-px bg-border/30 absolute" />
                <div className="w-1 h-3 bg-red-500 absolute top-1 rounded-full" />
                <div className="w-1 h-3 bg-white/30 absolute bottom-1 rounded-full" />
              </div>
              <div className="w-px h-6 bg-border mx-2" />
              <button 
                onClick={async () => {
                  if (mapRotationMode === 'north-up') {
                    requestCompassPermission();
                    setFollowMode(true);
                    setMapRotationMode('heading');
                  } else {
                    setMapRotationMode('north-up');
                  }
                }}
                className={`flex items-center gap-1.5 px-2 py-1 rounded-md border font-black text-[9px] uppercase tracking-wider transition-all ${mapRotationMode === 'heading' ? 'bg-accent text-bg border-accent shadow-lg shadow-accent/20' : 'bg-bg/50 text-text-dim border-border hover:text-text'}`}
              >
                <Navigation size={10} className={mapRotationMode === 'heading' ? 'fill-current' : ''} />
                {mapRotationMode === 'heading' ? 'Heading' : 'North'}
              </button>
              <button 
                onClick={() => setShowHeadingPanel(false)}
                className="p-0.5 ml-2 hover:bg-white/10 rounded-full transition-colors"
              >
                <X size={12} className="text-text-dim" />
              </button>
            </div>
          )}
        </div>
      )}'''

if header_end in content:
    # replace only the first occurrence to avoid destroying bottom elements
    content = content.replace(header_end, new_subheader, 1)
else:
    print("Could not find header_end!")
    sys.exit(1)

with open('src/App.tsx', 'w') as f:
    f.write(content)

print("SUCCESS")
