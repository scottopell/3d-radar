#version 460

// Inputs from Panda3D
uniform mat4 p3d_ViewMatrixInverse;
uniform mat4 p3d_ProjectionMatrixInverse;

// Inputs from program
uniform vec2 resolution;
uniform vec3 camera_position;

uniform vec3 bounds_start;
uniform vec3 bounds_end;

uniform sampler2D tex;

uniform mat4 trans_clip_to_view_of_myCameraNode;
uniform mat4 trans_world_to_model_of_myCameraNode;

uniform mat4 proj;

// Outputs to Panda3D
out vec4 p3d_FragColor;

const float NEAR = 1;
const float MAX_STEPS = 1000;
const float STEP_SIZE = 0.1; 

vec3 gen_ray() {
    float x = (2.0f * gl_FragCoord.x) / resolution.x - 1.0f;
    float y = (2.0f * gl_FragCoord.y) / resolution.y - 1.0f;
    
    vec4 ray_clip = vec4(x, y, -1.0, 1.0);
    vec4 ray_eye = p3d_ProjectionMatrixInverse * ray_clip;
    ray_eye = vec4(ray_eye.xy, -1.0, 0.0);

    vec3 ray_world = (p3d_ViewMatrixInverse * ray_eye).xyz;
    ray_world = normalize(ray_world);

    return ray_world;
}

vec3 gen_ray_2() {
    float x = (2.0f * gl_FragCoord.x) / resolution.x - 1.0f;
    float y = (2.0f * gl_FragCoord.y) / resolution.y - 1.0f;
    
    vec4 ray_clip = vec4(x, y, -1.0, 1.0);
    // vec4 ray_eye = (trans_clip_to_view_of_myCameraNode * ray_clip);
    vec4 ray_eye = (proj * ray_clip);
    ray_eye = vec4(ray_eye.xyz, 0.0);

    vec3 ray_world = (inverse(trans_world_to_model_of_myCameraNode) * ray_eye).xyz;
    ray_world = normalize(ray_world);

    return ray_world;
}

float density(in vec3 point, in vec3 center, float radius) {
    if (length(point - center) < radius) {
        return 1 - pow((length(point - center) / radius), 3.0f);
    }

    return 0.0;
}

vec4 blendOnto(vec4 cFront, vec4 cBehind) {
    return cFront + (1.0 - cFront.a)*cBehind;
}

void boxClip(
    in vec3 boxMin, in vec3 boxMax,
    in vec3 p, in vec3 v,
    out vec2 tRange, out float didHit
) {
    // For each coord, clip t to only contain values for which p+t*v is in range
    // More on this method here: https://tavianator.com/2011/ray_box.html
    vec3 tb0 = (boxMin - p) / v;
    vec3 tb1 = (boxMax - p) / v;
    vec3 tmin = min(tb0, tb1);
    vec3 tmax = max(tb0, tb1);

    tRange = vec2(
        max(max(tmin.x, tmin.y), tmin.z),
        min(min(tmax.x, tmax.y), tmax.z)
    );

    // 1 if tRange.s < t, 0 if tRange.s > t
    didHit = step(tRange.s, tRange.t);
}

vec4 ray_march(in vec3 ro, in vec3 rd) {
    vec2 tRange;
    float didHitBox;
    boxClip(bounds_start, bounds_end, ro, rd, tRange, didHitBox);

    // Make sure the range does not start behind the camera
    tRange.s = max(0.0, tRange.s);

    vec4 color = vec4(0.0);

    if (didHitBox < 0.5) {
        return color;
    }

    // TODO Add jitter, adjust near plane?
    float t = tRange.s;

    for (int i = 0; i < MAX_STEPS; i++) {
        // If we have moved out of the bounding box, exit the loop
        // TODO break loop when alpha has reached threshold
        if (t > tRange.t) {
            break;
        }

        vec3 sample_pos = ro + t * rd;

        float sample_density = density(sample_pos, vec3(0.0), 2.0);
        float sample_attenuation = exp(-STEP_SIZE * sample_density);
        vec3 sample_color = vec3(1.0 - sample_density, 0, sample_density);
        float sample_alpha = sample_density * STEP_SIZE;

        vec4 ci = vec4(sample_color, 1.0) * sample_alpha;
        color = blendOnto(color, ci);

        t += STEP_SIZE;
    }

    // TODO add compensation for early out for alpha
    
    return color;
}

vec4 ray_color(in vec3 rd) {
    return vec4(rd.x, rd.y, rd.z, 0.5);
}

void main() {
    vec4 scene_color = texelFetch(tex, ivec2(gl_FragCoord.xy), 0);
    // vec4 depth_pixel = texelFetch(dtex, ivec2(gl_FragCoord.xy), 0);

    vec3 ro = camera_position;
    vec3 rd = gen_ray();
    vec3 rd2 = gen_ray_2();

    vec4 shaded_color = ray_march(ro, rd2);
    // vec4 rc = ray_color(rd2);
    // if (gl_FragCoord.x > (resolution.x / 2)) {
    //     rc = ray_color(rd);
    // }
    // p3d_FragColor = rc;
    // p3d_FragColor = scene_color;
    // p3d_FragColor = shaded_color;
    p3d_FragColor = blendOnto(shaded_color, scene_color);
    // p3d_FragColor = blendOnto(rc, scene_color);
}