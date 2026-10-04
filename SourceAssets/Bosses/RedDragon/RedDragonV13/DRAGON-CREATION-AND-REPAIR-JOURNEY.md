# Dragon creation and repair journey

## Authority and starting defect

Sin requested believable walking, running and attacks in Studio on October 5,
2026. The former v1.1 preview contained 24 bones and six clips, no locomotion,
and stationary leg joints. Most motion came from rotating the wing/neck/tail
chains. The new revision preserves the original asset and the independent
v1.2 Vrax experiment; it does not retarget a humanoid onto the Dragon.

## Research applied

- [Wētā FX: Smaug](https://www.wetafx.co.nz/films/case-studies/smaug) describes
  building from the skeleton outward and using performance reference. Applied
  here: make an attack an intentional whole-body action, with a preparation,
  strike and recovery, instead of merely opening the mouth.
- [Framestore: How To Train Your Dragon](https://www.framestore.com/work/how-train-your-dragon)
  describes anatomical rigs, physical heft and references ranging from big cats
  and reptiles to bats and birds. Applied here: four distinct ground contacts,
  a moving torso above planted feet, and delayed appendage motion.
- [Simon Otto's first-person animation interview](https://www.artofvfx.com/dragons-simon-otto-responsable-animation-des-personnages-dreamworks/)
  explains mixing animal references to give each dragon its own behavior.
  Applied here: a heavy, deliberate walk and braced attacks for this armored
  quadruped, rather than copying Toothless or Smaug's anatomy or personality.

These are production accounts and reference principles, not a claim that this
small original rig matches a feature-film rig. No film animation or meshes were
downloaded or copied. The gait and attack curves are original authored data.

## Ownership

The self-contained Source directory holds the accepted v1.1 rig, original and
cleaned meshes, descriptor and reference art. The current `.blend` is a live
IK authoring rig. `animate.py` defines action beats and foot paths. The export
evaluates constraints, converts world poses into parent-local transforms, and
stores quaternion/location/scale keys on the 28 deformation bones. Controls
are excluded from GLB. The six established socket frames retain their rest
definitions and follow the new poses through Studio's existing owners.

## Review and refinement lessons

1. The first pole-angle sign bent knees toward the opposite side of the intended
   plane. Direct joint-position inspection and a three-quarter render exposed
   it. The corrected sign preserves the source's anatomical bend direction.
2. Lowering the torso without lifting the tail caused floor penetration. Lift
   the proximal tail from its own joint; do not raise the entire actor and make
   all feet float. The final common tail lift is nine degrees for this revision.
3. The lowest wing membrane vertices are much lower than the wing bones. Claw,
   roar and recoil exposed this. Evaluate deformed vertices, not only joints.
   Resting wing lift and the attack rotations were refined until all clips
   cleared the floor. Do not copy these angles to another dragon model.
4. Set 30 fps before reimporting GLB. Importing at Blender's default 24 fps and
   changing it afterward produced false loop/path failures. Export every action
   starting at zero so runtime impact cues stay aligned to authored seconds.
5. In-place gait stance moves backward linearly; swing follows a lifted return
   arc. World travel must use the documented gait speed if added later. Pinning
   a foot in actor-local space while translating the actor would cause skating.
6. Keep paws level independently of the shins. Smoothly transfer only the low
   claw weights into the four paw bones; preserve upper leg weights, geometry
   and UVs. Front leg chains inherit chest motion; IK compensates underneath it.

The final regression checks all eight clips in the exported GLB, including
first/last poses, every frame's floor clearance, attack foot drift, gait paths
and loop closure. There are no Block or Death actions in this package; do not
claim that those nonexistent clips were validated. Bind/Idle share the measured
floor baseline. The original texture and angular membrane topology impose an
art-quality limit that more keyframes alone cannot remove.
