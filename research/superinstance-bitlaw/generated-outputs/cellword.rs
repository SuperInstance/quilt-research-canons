// GENERATED from spec.json by bitlaw — do not edit by hand.
// Law: superinstance.cellword v2 — the u32 cell word IS the contract.
#[derive(Copy, Clone, Debug, Default, PartialEq, Eq)]
#[repr(transparent)]
pub struct CellWord(pub u32);

impl CellWord {
    pub const GLYPH_SHIFT: u32 = 0;
    pub const GLYPH_MASK: u32 = 0x000000FF;
    pub const ROUTE_SHIFT: u32 = 8;
    pub const ROUTE_MASK: u32 = 0x000000FF;
    pub const WEIGHT_SHIFT: u32 = 16;
    pub const WEIGHT_MASK: u32 = 0x000000FF;
    pub const FLAGS_SHIFT: u32 = 24;
    pub const FLAGS_MASK: u32 = 0x0000000F;
    pub const BUZZ_SHIFT: u32 = 28;
    pub const BUZZ_MASK: u32 = 0x0000000F;

    #[inline(always)]
    pub fn pack(glyph: u8, route: u8, weight: u8, flags: u8, buzz: u8) -> Self {
        Self(
            (glyph as u32) & Self::GLYPH_MASK
            | (((route as u32) & Self::ROUTE_MASK) << Self::ROUTE_SHIFT)
            | (((weight as u32) & Self::WEIGHT_MASK) << Self::WEIGHT_SHIFT)
            | (((flags as u32) & Self::FLAGS_MASK) << Self::FLAGS_SHIFT)
            | (((buzz as u32) & Self::BUZZ_MASK) << Self::BUZZ_SHIFT)
        )
    }

    #[inline(always)]
    pub fn unpack(self) -> (u8, u8, u8, u8, u8) {
        (
            ((self.0 >> Self::GLYPH_SHIFT) & Self::GLYPH_MASK) as u8,
            ((self.0 >> Self::ROUTE_SHIFT) & Self::ROUTE_MASK) as u8,
            ((self.0 >> Self::WEIGHT_SHIFT) & Self::WEIGHT_MASK) as u8,
            ((self.0 >> Self::FLAGS_SHIFT) & Self::FLAGS_MASK) as u8,
            ((self.0 >> Self::BUZZ_SHIFT) & Self::BUZZ_MASK) as u8,
        )
    }
}
