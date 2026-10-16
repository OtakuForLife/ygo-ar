shader_type spatial;
render_mode cull_disabled, diffuse_toon, specular_disabled, depth_test_disabled, ambient_light_disabled, unshaded, blend_mix, depth_draw_opaque, shadows_disabled;

uniform sampler2D back_sprite: source_color;
uniform sampler2D front_sprite: source_color;

void fragment() {
	
	vec4 back = texture(back_sprite, UV.xy);
	vec3 back_rgb = back.rgb;
	//float back_alpha = back.a;
	
	vec4 front = texture(front_sprite, UV.xy);
	vec3 front_rgb = front.rgb;
	//float front_alpha = front.a;
	
	bool is_front = FRONT_FACING;
	
	vec3 mixed_out = mix(back_rgb, front_rgb, vec3(is_front ? 1.0 : 0.0));
	
	ALBEDO = mixed_out;
	
}