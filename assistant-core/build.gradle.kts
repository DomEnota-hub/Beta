plugins {
    id("org.jetbrains.kotlin.jvm")
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    implementation(project(":domain-contracts"))
    implementation(project(":content-runtime"))
    testImplementation("junit:junit:4.13.2")
}
